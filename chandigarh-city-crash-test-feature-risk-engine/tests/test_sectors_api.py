from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_get_sectors():
    response = client.get("/api/sectors")
    assert response.status_code == 200
    data = response.json()
    assert data["data_status"] == "synthetic_demo"
    assert data["score_label"] == "Unvalidated demo index (0-100)"
    assert data["total_sectors"] >= 5
    assert len(data["sectors"]) == data["total_sectors"]
    
    # Verify key Chandigarh sectors are included
    sector_ids = [s["sector_id"] for s in data["sectors"]]
    assert "sector-17" in sector_ids
    assert "sector-22" in sector_ids
    assert "sector-35" in sector_ids
    assert "sector-26" in sector_ids

    # Verify GeoJSON payload exists
    assert data["geojson"] is not None
    assert data["geojson"]["type"] == "FeatureCollection"
