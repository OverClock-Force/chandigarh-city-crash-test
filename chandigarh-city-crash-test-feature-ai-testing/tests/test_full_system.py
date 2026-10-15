import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from ai_intake.extractor import ComplaintExtractor

client = TestClient(app)


def test_root_and_health():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert data["data_status"] == "synthetic_demo"

    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["data_status"] == "synthetic_demo"


def test_sectors_and_spatial_data():
    res = client.get("/api/sectors")
    assert res.status_code == 200
    data = res.json()
    assert data["data_status"] == "synthetic_demo"
    assert data["total_sectors"] >= 10
    assert data["geojson"]["type"] == "FeatureCollection"
    assert len(data["geojson"]["features"]) >= 5


def test_events_lifecycle():
    res = client.get("/api/events")
    assert res.status_code == 200
    initial_count = res.json()["total_events"]
    assert initial_count > 0

    new_event = {
        "category": "drainage_blockage",
        "severity": "high",
        "sector_id": "sector-17",
        "location_description": "Road gully choked near Plaza fountain",
        "source": "automated_test",
        "confidence": 0.95
    }
    create_res = client.post("/api/events", json=new_event)
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["sector_id"] == "sector-17"
    assert created["category"] == "drainage_blockage"

    # Test filtering by sector_id
    filter_res = client.get("/api/events?sector_id=sector-17")
    assert filter_res.status_code == 200
    filtered_events = filter_res.json()["events"]
    assert any(e["event_id"] == created["event_id"] for e in filtered_events)


def test_stress_test_simulation():
    scenario = {
        "rainfall_mm": 60.0,
        "rainfall_duration_hours": 2.0,
        "debris_level": "high",
        "drain_condition": "partial_blockage",
        "traffic_level": "peak",
        "temperature_c": 38.0,
        "resources": {
            "maintenance_teams": 4,
            "pumping_units": 2,
            "budget_inr": 350000.0
        }
    }
    res = client.post("/api/stress-test", json=scenario)
    assert res.status_code == 200
    sim = res.json()
    assert sim["data_status"] == "synthetic_demo"
    assert sim["score_label"] == "Unvalidated demo index (0-100)"
    assert 0 <= sim["overall_score"] <= 100
    assert "components" in sim
    assert sim["components"]["drainage_stress"] > 0
    assert sim["components"]["waterlogging"] > 0
    assert len(sim["cascade"]) >= 4

    # Verify each cascade link
    for link in sim["cascade"]:
        assert link["evidence_status"] in ["modeled", "hypothetical"]
        assert 0.0 <= link["intensity"] <= 1.0


def test_input_validation_boundaries():
    # Rainfall > 100mm should fail
    high_rain = {
        "rainfall_mm": 120.0,
        "debris_level": "high",
        "drain_condition": "partial_blockage",
        "traffic_level": "peak",
        "temperature_c": 38.0
    }
    assert client.post("/api/stress-test", json=high_rain).status_code == 422

    # Rainfall < 15mm should fail
    low_rain = {
        "rainfall_mm": 10.0,
        "debris_level": "high",
        "drain_condition": "partial_blockage",
        "traffic_level": "peak",
        "temperature_c": 38.0
    }
    assert client.post("/api/stress-test", json=low_rain).status_code == 422


def test_intervention_optimizer():
    scenario = {
        "rainfall_mm": 60.0,
        "debris_level": "high",
        "drain_condition": "partial_blockage",
        "traffic_level": "peak",
        "temperature_c": 38.0,
        "resources": {
            "maintenance_teams": 4,
            "pumping_units": 2,
            "budget_inr": 350000.0
        }
    }
    res = client.post("/api/optimize", json=scenario)
    assert res.status_code == 200
    opt = res.json()
    assert opt["data_status"] == "synthetic_demo"
    rec = opt["recommended_action"]
    assert rec["is_feasible"] is True
    assert rec["risk_reduction"] > 0
    assert rec["utility_score"] > 0
    assert rec["resources_remaining"]["maintenance_teams"] >= 0
    assert rec["resources_remaining"]["pumping_units"] >= 0
    assert rec["resources_remaining"]["budget_inr"] >= 0


def test_scenarios_persistence():
    scenario = {
        "rainfall_mm": 55.0,
        "debris_level": "normal",
        "drain_condition": "good",
        "traffic_level": "normal",
        "temperature_c": 35.0,
        "resources": {
            "maintenance_teams": 2,
            "pumping_units": 1,
            "budget_inr": 200000.0
        }
    }
    save_res = client.post("/api/scenarios", json=scenario)
    assert save_res.status_code == 201
    saved_id = save_res.json()["scenario_id"]

    get_res = client.get(f"/api/scenarios/{saved_id}")
    assert get_res.status_code == 200
    assert get_res.json()["scenario_id"] == saved_id

    assert client.get("/api/scenarios/non-existent-xyz").status_code == 404


def test_ai_intake_extractor():
    extractor = ComplaintExtractor()
    res = extractor.extract("Severe road gully blockage near Sector 17 plaza fountain, water is pooling fast.")
    assert res.category == "drainage_blockage"
    assert res.severity == "high"
    assert res.sector_id == "sector-17"
    assert res.user_must_confirm is True

    # When no sector is mentioned, it must NOT guess
    res_no_sec = extractor.extract("Heavy plastic waste and leaf litter choking drainage line.")
    assert res_no_sec.sector_id is None
    assert res_no_sec.user_must_confirm is True


def test_openapi_and_docs():
    assert client.get("/openapi.json").status_code == 200
    assert client.get("/docs").status_code == 200
