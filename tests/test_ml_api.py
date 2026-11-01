import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_ml_suite_endpoint():
    response = client.get("/api/ml/suite")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "models" in data
    assert "k_means" in data["models"]
    assert "decision_tree" in data["models"]
    assert "linear_regression" in data["models"]
    assert len(data["report_highlights"]) >= 3


def test_kmeans_clustering_endpoint():
    response = client.get("/api/ml/clustering?n_clusters=3")
    assert response.status_code == 200
    data = response.json()
    assert data["algorithm"] == "K-Means Clustering"
    assert data["n_clusters"] == 3
    assert len(data["clusters"]) == 3
    assert len(data["sectors"]) > 0
    assert "inertia" in data


def test_decision_tree_endpoint():
    response = client.get("/api/ml/decision-tree?max_depth=4")
    assert response.status_code == 200
    data = response.json()
    assert data["algorithm"] == "Decision Tree Classifier"
    assert "accuracy" in data
    assert "feature_importances" in data
    assert "text_rules" in data


def test_linear_regression_endpoint():
    response = client.get("/api/ml/regression")
    assert response.status_code == 200
    data = response.json()
    assert data["algorithm"] == "Multiple Linear Regression"
    assert "r2_score" in data
    assert "mse" in data
    assert "coefficients" in data
    assert "regression_equation" in data


def test_predict_regression_endpoint():
    response = client.post(
        "/api/ml/predict-regression",
        json={
            "rainfall_mm": 65.0,
            "drain_factor": 0.60,
            "debris_factor": 0.65,
            "traffic_factor": 0.85
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "predicted_risk_score" in data
    assert 0.0 <= data["predicted_risk_score"] <= 100.0


def test_predict_tree_endpoint():
    response = client.post(
        "/api/ml/predict-tree",
        json={
            "rainfall_mm": 80.0,
            "debris_level": "extreme",
            "drain_condition": "critical",
            "traffic_level": "peak",
            "sector_id": "sector-17"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "predicted_category" in data
    assert data["predicted_category"] in ["low", "moderate", "high", "severe"]
