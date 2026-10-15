from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_stress_test_default_60mm():
    payload = {
        "rainfall_mm": 60.0,
        "rainfall_duration_hours": None,
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
    response = client.post("/api/stress-test", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["data_status"] == "synthetic_demo"
    assert data["score_label"] == "Unvalidated demo index (0-100)"
    assert 0.0 <= data["overall_score"] <= 100.0
    
    # Check components
    components = data["components"]
    assert "drainage_stress" in components
    assert "waterlogging" in components
    assert "road_traffic" in components
    assert "emergency_access" in components
    assert "heat_stress_context" in components

    # Check sectors breakdown
    assert len(data["sectors"]) > 0
    first_sector = data["sectors"][0]
    assert "sector_id" in first_sector
    assert "score" in first_sector
    assert "main_factors" in first_sector

    # Check cascade
    assert len(data["cascade"]) > 0
    first_edge = data["cascade"][0]
    assert "from" in first_edge
    assert "to" in first_edge
    assert first_edge["evidence_status"] in ["modeled", "hypothetical"]

    # Check assumptions
    assert len(data["assumptions"]) > 0


def test_stress_test_invalid_inputs():
    # Rainfall below 15mm
    res_low_rain = client.post("/api/stress-test", json={
        "rainfall_mm": 10.0,
        "debris_level": "high",
        "drain_condition": "partial_blockage",
        "traffic_level": "peak",
        "temperature_c": 38.0
    })
    assert res_low_rain.status_code == 422
    assert "field_errors" in res_low_rain.json()

    # Rainfall above 100mm
    res_high_rain = client.post("/api/stress-test", json={
        "rainfall_mm": 120.0,
        "debris_level": "high",
        "drain_condition": "partial_blockage",
        "traffic_level": "peak",
        "temperature_c": 38.0
    })
    assert res_high_rain.status_code == 422

    # Invalid debris level
    res_invalid_debris = client.post("/api/stress-test", json={
        "rainfall_mm": 50.0,
        "debris_level": "catastrophic",
        "drain_condition": "partial_blockage",
        "traffic_level": "peak",
        "temperature_c": 38.0
    })
    assert res_invalid_debris.status_code == 422

    # Temperature out of bounds (below 32C)
    res_invalid_temp = client.post("/api/stress-test", json={
        "rainfall_mm": 50.0,
        "debris_level": "high",
        "drain_condition": "partial_blockage",
        "traffic_level": "peak",
        "temperature_c": 22.0
    })
    assert res_invalid_temp.status_code == 422
