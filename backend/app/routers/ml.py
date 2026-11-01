"""
Router: Machine Learning Analytics Suite
Provides endpoints for K-Means Clustering, Decision Tree Classification, and Multiple Linear Regression.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from risk_engine.ml_suite import (
    run_full_ml_suite,
    kmeans_service,
    decision_tree_service,
    linear_regressor_service,
    load_sectors_data,
)

router = APIRouter(prefix="/api/ml", tags=["Machine Learning"])


class RegressionPredictRequest(BaseModel):
    rainfall_mm: float = Field(default=45.0, ge=15.0, le=100.0)
    drain_factor: float = Field(default=0.60, ge=0.0, le=1.0)
    debris_factor: float = Field(default=0.65, ge=0.0, le=1.0)
    traffic_factor: float = Field(default=0.85, ge=0.0, le=1.0)


class TreePredictRequest(BaseModel):
    rainfall_mm: float = Field(default=55.0, ge=15.0, le=100.0)
    debris_level: str = Field(default="high")
    drain_condition: str = Field(default="partial_blockage")
    traffic_level: str = Field(default="peak")
    sector_id: Optional[str] = Field(default="sector-17")


@router.get("/suite", summary="Full ML Analytics Report (K-Means, Decision Tree, Linear Regression)")
def get_ml_suite() -> Dict[str, Any]:
    """
    Executes and returns a complete evaluation of all 3 classical ML models:
    - K-Means Clustering (Sector Vulnerability Clusters)
    - Decision Tree Classifier (Severity Classification & Decision Rules)
    - Multiple Linear Regression (Risk Equation, R² & Beta Coefficients)
    """
    return run_full_ml_suite()


@router.get("/clustering", summary="K-Means Clustering on Chandigarh Sectors")
def get_kmeans_clustering(n_clusters: int = Query(default=3, ge=2, le=5)) -> Dict[str, Any]:
    """
    Partitions Chandigarh sectors into multi-attribute vulnerability clusters.
    """
    sectors = load_sectors_data()
    from risk_engine.ml_suite import KMeansSectorClusterer
    clusterer = KMeansSectorClusterer(n_clusters=n_clusters)
    return clusterer.fit_predict(sectors)


@router.get("/decision-tree", summary="Decision Tree Risk Severity Classifier")
def get_decision_tree(max_depth: int = Query(default=4, ge=2, le=8)) -> Dict[str, Any]:
    """
    Trains and explains the Decision Tree Classifier for low/moderate/high/severe risk classification.
    """
    sectors = load_sectors_data()
    from risk_engine.ml_suite import DecisionTreeRiskClassifier
    tree = DecisionTreeRiskClassifier(max_depth=max_depth)
    return tree.train_and_explain(sectors)


@router.get("/regression", summary="Multiple Linear Regression Model")
def get_linear_regression() -> Dict[str, Any]:
    """
    Fits and evaluates Multiple Linear Regression predicting continuous risk score from rainfall, drain blockage, debris, and traffic.
    """
    return linear_regressor_service.train_and_evaluate()


@router.post("/predict-regression", summary="Predict Risk Score using Linear Regression")
def predict_regression(req: RegressionPredictRequest) -> Dict[str, Any]:
    pred_score = linear_regressor_service.predict(
        rainfall_mm=req.rainfall_mm,
        drain_factor=req.drain_factor,
        debris_factor=req.debris_factor,
        traffic_factor=req.traffic_factor
    )
    return {
        "model": "Multiple Linear Regression",
        "predicted_risk_score": pred_score,
        "inputs": req.model_dump(),
        "equation": linear_regressor_service.train_and_evaluate()["regression_equation"]
    }


@router.post("/predict-tree", summary="Predict Risk Severity using Decision Tree")
def predict_tree(req: TreePredictRequest) -> Dict[str, Any]:
    sectors = load_sectors_data()
    matched = next((s for s in sectors if s["sector_id"] == req.sector_id), sectors[0])
    # Ensure tree is fitted
    decision_tree_service.train_and_explain(sectors)
    result = decision_tree_service.predict_scenario_sector(req.model_dump(), matched)
    return {
        "model": "Decision Tree Classifier",
        "sector_id": matched["sector_id"],
        "sector_name": matched["name"],
        **result
    }
