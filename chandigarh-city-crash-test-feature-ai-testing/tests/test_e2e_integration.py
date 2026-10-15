import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from ai_intake.extractor import ComplaintExtractor

client = TestClient(app)


def test_e2e_stress_test_and_optimization_pipeline():
    """
    Validates Milestone M3 Exit Criteria:
    Default scenario works from input to results to intervention comparison with resource bounds.
    """
    # 1. Probe health
    health_res = client.get("/health")
    assert health_res.status_code == 200
    assert health_res.json()["data_status"] == "synthetic_demo"

    # 2. Retrieve sectors
    sectors_res = client.get("/api/sectors")
    assert sectors_res.status_code == 200
    sectors_data = sectors_res.json()
    assert sectors_data["data_status"] == "synthetic_demo"
    assert len(sectors_data["sectors"]) >= 10

    # 3. Execute standard 60mm stress test scenario
    scenario_payload = {
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
    sim_res = client.post("/api/stress-test", json=scenario_payload)
    assert sim_res.status_code == 200
    sim_data = sim_res.json()

    assert sim_data["data_status"] == "synthetic_demo"
    assert sim_data["score_label"] == "Unvalidated demo index (0-100)"
    assert "overall_score" in sim_data
    assert "cascade" in sim_data
    assert len(sim_data["cascade"]) >= 4

    # Verify every cascade link has evidence status and intensity
    for link in sim_data["cascade"]:
        assert link["evidence_status"] in ["modeled", "hypothetical"]
        assert 0.0 <= link["intensity"] <= 1.0

    # 4. Execute intervention optimization
    opt_res = client.post("/api/optimize", json=scenario_payload)
    assert opt_res.status_code == 200
    opt_data = opt_res.json()

    assert opt_data["data_status"] == "synthetic_demo"
    assert "recommended_action" in opt_data
    assert opt_data["recommended_action"]["is_feasible"] is True
    assert opt_data["recommended_action"]["risk_reduction"] > 0
    assert "resources_remaining" in opt_data["recommended_action"]

    # 5. Citizen incident report intake
    report_payload = {
        "category": "drainage_blockage",
        "severity": "high",
        "sector_id": "sector-17",
        "location_description": "Road gully grating choked near Plaza fountain",
        "source": "citizen_mobile",
        "confidence": 0.95
    }
    report_res = client.post("/api/events", json=report_payload)
    assert report_res.status_code == 201
    event_data = report_res.json()
    assert event_data["category"] == "drainage_blockage"
    assert event_data["sector_id"] == "sector-17"


def test_ai_intake_extraction_and_safety_rules():
    """
    Validates Milestone M4 Optional AI Intake:
    Extracts category and severity, user must confirm every field, and NEVER guesses location.
    """
    extractor = ComplaintExtractor()

    # Case 1: Explicit sector mentioned
    text_with_sector = "Severe road gully blockage near Sector 17 plaza fountain, water is pooling fast."
    res1 = extractor.extract(text_with_sector)
    assert res1.category == "drainage_blockage"
    assert res1.severity == "high"
    assert res1.sector_id == "sector-17"
    assert res1.user_must_confirm is True

    # Case 2: Location NOT mentioned (STRICT: Never guess location)
    text_without_sector = "There is huge garbage accumulation and plastic waste clogging the main sewer line."
    res2 = extractor.extract(text_without_sector)
    assert res2.category in ["waste_hotspot", "drainage_blockage"]
    assert res2.sector_id is None  # Strictly None, never guessed
    assert "No explicit sector found" in res2.notes
    assert res2.user_must_confirm is True
