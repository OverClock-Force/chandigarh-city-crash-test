from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_list_and_create_events():
    # 1. List initial events
    res_list = client.get("/api/events")
    assert res_list.status_code == 200
    data = res_list.json()
    assert data["total_events"] >= 4
    initial_count = data["total_events"]

    # 2. Filter by sector
    res_filtered = client.get("/api/events?sector_id=sector-17")
    assert res_filtered.status_code == 200
    filt_data = res_filtered.json()
    for ev in filt_data["events"]:
        assert ev["sector_id"] == "sector-17"

    # 3. Create a new event
    new_event = {
        "category": "drainage_blockage",
        "severity": "high",
        "sector_id": "sector-22",
        "location_description": "Underground storm culvert clogged near market parking entrance",
        "source": "citizen_mobile",
        "confidence": 0.95
    }
    res_create = client.post("/api/events", json=new_event)
    assert res_create.status_code == 201
    created_data = res_create.json()
    assert created_data["event_id"].startswith("evt-")
    assert created_data["sector_id"] == "sector-22"
    assert created_data["status"] == "unverified"

    # 4. Check list length increased
    res_list_after = client.get("/api/events")
    assert res_list_after.json()["total_events"] == initial_count + 1
