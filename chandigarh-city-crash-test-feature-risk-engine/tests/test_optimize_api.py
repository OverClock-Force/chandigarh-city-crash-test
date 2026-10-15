from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_optimize_endpoint_with_feasible_actions():
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
    response = client.post("/api/optimize", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["data_status"] == "synthetic_demo"
    assert "baseline_score" in data
    assert "recommended_action" in data
    assert "all_evaluations" in data

    rec = data["recommended_action"]
    assert rec["is_feasible"] is True
    assert rec["modeled_risk_score"] <= data["baseline_score"]
    assert rec["risk_reduction"] >= 0.0

    # Ensure resource bounds are respected
    used = rec["resources_used"]
    assert used["maintenance_teams"] <= payload["resources"]["maintenance_teams"]
    assert used["pumping_units"] <= payload["resources"]["pumping_units"]
    assert used["budget_inr"] <= payload["resources"]["budget_inr"]

    # Verify Do Nothing baseline exists in evaluations
    action_ids = [e["action_id"] for e in data["all_evaluations"]]
    assert "do_nothing" in action_ids


def test_optimize_endpoint_budget_exhausted():
    payload = {
        "rainfall_mm": 60.0,
        "rainfall_duration_hours": None,
        "debris_level": "high",
        "drain_condition": "partial_blockage",
        "traffic_level": "peak",
        "temperature_c": 38.0,
        "resources": {
            "maintenance_teams": 0,
            "pumping_units": 0,
            "budget_inr": 0.0
        }
    }
    response = client.post("/api/optimize", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Recommended must be do_nothing when 0 resources are provided
    assert data["recommended_action"]["action_id"] == "do_nothing"
