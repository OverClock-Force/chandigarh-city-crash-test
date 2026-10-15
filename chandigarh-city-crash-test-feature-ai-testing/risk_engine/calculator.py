from typing import List, Dict, Tuple
import uuid
from .models import (
    ScenarioInput,
    ComponentScores,
    SectorRiskScore,
    SectorData,
    RiskAssessmentResult,
)
from .cascade import generate_cascade_graph

# Numeric mappings for categorical inputs
DEBRIS_FACTORS = {
    "normal": 0.20,
    "high": 0.65,
    "extreme": 1.00,
}

DRAIN_FACTORS = {
    "good": 0.15,
    "partial_blockage": 0.60,
    "critical": 0.95,
}

TRAFFIC_FACTORS = {
    "normal": 0.30,
    "peak": 0.85,
}


def compute_component_scores(scenario: ScenarioInput) -> ComponentScores:
    """
    Computes transparent rule-based component scores based on calibrated empirical heuristics.
    Enforces the documented rule: Temperature is an independent heat pathway and does not raise flood risk.
    """
    # 1. Normalize rainfall (strictly 15 to 100 mm)
    rain_normalized = (scenario.rainfall_mm - 15.0) / (100.0 - 15.0)  # 0.0 to 1.0
    
    # Duration intensity adjustment if provided
    if scenario.rainfall_duration_hours and scenario.rainfall_duration_hours > 0:
        # Intensity in mm/hr
        intensity = scenario.rainfall_mm / scenario.rainfall_duration_hours
        # 30mm/hr+ is considered high intensity cloudburst-like in urban drainage
        intensity_modifier = min(1.3, max(0.8, intensity / 25.0))
        rain_effective = min(1.0, rain_normalized * intensity_modifier)
    else:
        rain_effective = rain_normalized

    debris_factor = DEBRIS_FACTORS[scenario.debris_level]
    drain_factor = DRAIN_FACTORS[scenario.drain_condition]
    traffic_factor = TRAFFIC_FACTORS[scenario.traffic_level]

    # Normalize heat (strictly 32 to 43 C)
    heat_factor = (scenario.temperature_c - 32.0) / (43.0 - 32.0)

    # Component 1: Drainage Stress (rain + drain condition + debris blocking gullies)
    # Weights: 45% rain, 30% drain baseline condition, 25% debris load
    drainage_stress = min(100.0, 100.0 * (
        0.45 * rain_effective +
        0.30 * drain_factor +
        0.25 * debris_factor
    ))

    # Component 2: Waterlogging Risk (drainage stress exceeds outflow capacity + debris)
    # Weights: 50% drainage stress, 35% rain intensity, 15% debris blockage
    waterlogging = min(100.0, 100.0 * (
        0.50 * (drainage_stress / 100.0) +
        0.35 * rain_effective +
        0.15 * debris_factor
    ))

    # Component 3: Road Traffic Disruption (baseline traffic exacerbated by waterlogged lanes)
    # Weights: 45% traffic load, 40% waterlogging, 15% drainage stress
    road_traffic = min(100.0, 100.0 * (
        0.45 * traffic_factor +
        0.40 * (waterlogging / 100.0) +
        0.15 * (drainage_stress / 100.0)
    ))

    # Component 4: Emergency Access Delay (traffic gridlock + impassable waterlogged nodes)
    # Weights: 60% road traffic, 40% waterlogging
    emergency_access = min(100.0, 100.0 * (
        0.60 * (road_traffic / 100.0) +
        0.40 * (waterlogging / 100.0)
    ))

    # Component 5: Heat Stress Context (independent environmental monitoring pathway)
    heat_stress_context = round(heat_factor * 100.0, 1)

    return ComponentScores(
        drainage_stress=round(drainage_stress, 1),
        waterlogging=round(waterlogging, 1),
        road_traffic=round(road_traffic, 1),
        emergency_access=round(emergency_access, 1),
        heat_stress_context=heat_stress_context,
    )


def calculate_sector_scores(
    components: ComponentScores,
    scenario: ScenarioInput,
    sectors_data: List[SectorData]
) -> List[SectorRiskScore]:
    """
    Distributes citywide stress onto specific sectors based on local topography,
    drainage vulnerability, road exposure, and historical hotspot status.
    """
    sector_scores: List[SectorRiskScore] = []

    for sector in sectors_data:
        # Local multipliers
        hotspot_boost = 15.0 if sector.is_historic_hotspot else 0.0
        
        # Sector specific drainage stress
        local_drain = components.drainage_stress * (0.6 + 0.8 * sector.drain_vulnerability)
        
        # Sector specific waterlogging (boosted by lower elevation / bowl depressions)
        local_water = components.waterlogging * (0.5 + 0.7 * sector.elevation_factor + 0.3 * sector.waste_pressure)
        
        # Sector specific traffic disruption (boosted by arterial junction exposure)
        local_traffic = components.road_traffic * (0.6 + 0.7 * sector.road_exposure)
        
        # Combined localized score
        raw_sector_score = (
            0.35 * local_water +
            0.25 * local_drain +
            0.25 * local_traffic +
            0.15 * components.emergency_access +
            hotspot_boost
        )
        sector_score = min(100.0, max(5.0, round(raw_sector_score, 1)))

        # Categorize
        if sector_score >= 75.0:
            category = "severe"
        elif sector_score >= 50.0:
            category = "high"
        elif sector_score >= 30.0:
            category = "moderate"
        else:
            category = "low"

        # Explainable factors
        main_factors = []
        if sector.is_historic_hotspot:
            main_factors.append("Documented recurring monsoon waterlogging hotspot (Chandigarh MC 2026)")
        if sector.drain_vulnerability > 0.6:
            main_factors.append(f"High storm-drain vulnerability & gully blockage susceptibility ({scenario.drain_condition})")
        if sector.elevation_factor > 0.6:
            main_factors.append("Low-lying topographic depression prone to surface runoff pooling")
        if sector.waste_pressure > 0.6 and scenario.debris_level in ["high", "extreme"]:
            main_factors.append(f"Commercial/market waste load exacerbating intake grate clogging ({scenario.debris_level})")
        if sector.road_exposure > 0.6 and scenario.traffic_level == "peak":
            main_factors.append("High arterial vehicle density causing cascading intersection gridlock")
        if not main_factors:
            main_factors.append("Moderate localized runoff with functional gravity drainage")

        sector_scores.append(SectorRiskScore(
            sector_id=sector.sector_id,
            sector_name=sector.name,
            score=sector_score,
            category=category,
            main_factors=main_factors
        ))

    # Sort highest risk sectors first
    sector_scores.sort(key=lambda s: s.score, reverse=True)
    return sector_scores


def calculate_scenario_risk(
    scenario: ScenarioInput,
    sectors_data: List[SectorData]
) -> RiskAssessmentResult:
    """
    Executes full risk engine assessment pipeline:
    components -> sector breakdown -> cascade graph -> assumptions.
    """
    scenario_id = scenario.scenario_id or f"scen-{uuid.uuid4().hex[:8]}"
    components = compute_component_scores(scenario)

    # Citywide overall score
    # Waterlogging & drainage form majority, traffic & emergency access cascade follow
    overall = (
        0.35 * components.waterlogging +
        0.25 * components.drainage_stress +
        0.20 * components.road_traffic +
        0.15 * components.emergency_access +
        0.05 * components.heat_stress_context
    )
    overall_score = round(min(100.0, max(0.0, overall)), 1)

    sectors = calculate_sector_scores(components, scenario, sectors_data)
    cascade = generate_cascade_graph(scenario, components)

    assumptions = [
        "Unvalidated heuristic model for hackathon decision exploration only.",
        "Rainfall runoff response assumes standard Chandigarh urban impervious surface ratio (~65-75%).",
        "Temperature is computed as an independent heat-stress pathway and intentionally decoupled from flood mechanics.",
        "Hotspot vulnerabilities calibrated against reported Chandigarh MC 2026 waterlogging assessments.",
        "Resource allocation assumes immediate deployment without travel transit latency."
    ]

    return RiskAssessmentResult(
        scenario_id=scenario_id,
        data_status="synthetic_demo",
        score_label="Unvalidated demo index (0-100)",
        overall_score=overall_score,
        components=components,
        sectors=sectors,
        cascade=cascade,
        assumptions=assumptions
    )
