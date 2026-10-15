from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_list_and_save_scenarios():
    # 1. List scenarios
    res_list = client.get("/api/scenarios")
    assert res_list.status_code == 200
    data = res_list.json()
    assert data["total_scenarios"] >= 3
    initial_count = data["total_scenarios"]

    # 2. Get specific scenario
    res_get = client.get("/api/scenarios/scen-default-60mm")
    assert res_get.status_code == 200
    scen = res_get.json()
    assert scen["scenario_id"] == "scen-default-60mm"
    assert scen["rainfall_mm"] == 60.0

    # 3. Save a custom scenario
    custom_scen = {
        "scenario_id": "scen-custom-test-1",
        "title": "Custom High-Tide Flash Storm",
        "rainfall_mm": 80.0,
        "rainfall_duration_hours": 1.0,
        "debris_level": "extreme",
        "drain_condition": "critical",
        "traffic_level": "peak",
        "temperature_c": 35.0,
        "resources": {
            "maintenance_teams": 5,
            "pumping_units": 3,
            "budget_inr": 450000.0
        }
    }
    res_save = client.post("/api/scenarios", json=custom_scen)
    assert res_save.status_code == 201
    saved = res_save.json()
    assert saved["scenario_id"] == "scen-custom-test-1"

    # 4. Retrieve saved scenario
    res_get_saved = client.get("/api/scenarios/scen-custom-test-1")
    assert res_get_saved.status_code == 200
    assert res_get_saved.json()["title"] == "Custom High-Tide Flash Storm"


def test_get_nonexistent_scenario():
    res = client.get("/api/scenarios/scen-nonexistent-999")
    assert res.status_code == 404
