from typing import List
from .models import ScenarioInput, ComponentScores, CascadeLink


def generate_cascade_graph(
    scenario: ScenarioInput,
    components: ComponentScores
) -> List[CascadeLink]:
    """
    Generates the cross-domain causal failure chain.
    Each link explicitly carries evidence_status ('modeled' or 'hypothetical')
    and relative transfer intensity.
    """
    cascade: List[CascadeLink] = []

    # 1. Rainfall -> Drainage Stress
    rain_weight = min(1.0, scenario.rainfall_mm / 100.0)
    cascade.append(CascadeLink(
        **{
            "from": f"Rainfall ({scenario.rainfall_mm}mm)",
            "to": "Drainage System Stress",
            "evidence_status": "modeled",
            "intensity": round(rain_weight, 2),
            "description": f"Precipitation volume ({scenario.rainfall_mm}mm) approaches or exceeds stormwater carrying capacity"
        }
    ))

    # 2. Debris accumulation -> Reduced Inlet Capacity
    if scenario.debris_level in ["high", "extreme"]:
        cascade.append(CascadeLink(
            **{
                "from": f"Debris Accumulation ({scenario.debris_level})",
                "to": "Drainage System Stress",
                "evidence_status": "modeled",
                "intensity": 0.85 if scenario.debris_level == "extreme" else 0.65,
                "description": "Solid waste and fallen leaf litter block road-gully gratings and curb inlets"
            }
        ))

    # 3. Drain Condition -> Drainage System Stress
    if scenario.drain_condition != "good":
        cascade.append(CascadeLink(
            **{
                "from": f"Drain Infrastructure ({scenario.drain_condition})",
                "to": "Drainage System Stress",
                "evidence_status": "modeled",
                "intensity": 0.90 if scenario.drain_condition == "critical" else 0.60,
                "description": "Structural siltation or damage lowers pipe conveyance velocity"
            }
        ))

    # 4. Drainage System Stress -> Surface Waterlogging
    waterlogging_intensity = min(1.0, components.drainage_stress / 100.0)
    cascade.append(CascadeLink(
        **{
            "from": "Drainage System Stress",
            "to": "Surface Waterlogging Hotspots",
            "evidence_status": "modeled",
            "intensity": round(waterlogging_intensity, 2),
            "description": "Uncollected stormwater backs up onto carriageways and roundabouts"
        }
    ))

    # 5. Surface Waterlogging -> Road Traffic Disruption
    traffic_intensity = min(1.0, components.waterlogging / 100.0 * 0.9)
    cascade.append(CascadeLink(
        **{
            "from": "Surface Waterlogging Hotspots",
            "to": "Road Traffic Disruption",
            "evidence_status": "modeled",
            "intensity": round(traffic_intensity, 2),
            "description": f"Flooded lane sections throttle vehicle speeds ({scenario.traffic_level} traffic baseline)"
        }
    ))

    # 6. Road Traffic Disruption -> Emergency Access Delay
    emergency_intensity = min(1.0, (components.road_traffic / 100.0) * 0.85)
    cascade.append(CascadeLink(
        **{
            "from": "Road Traffic Disruption",
            "to": "Emergency Response Access Delay",
            "evidence_status": "hypothetical",
            "intensity": round(emergency_intensity, 2),
            "description": "Ambulance and fire corridor transit times degrade due to arterial choke points"
        }
    ))

    # 7. Independent Heat Pathway
    if scenario.temperature_c >= 35.0:
        heat_intensity = min(1.0, (scenario.temperature_c - 32.0) / 11.0)
        cascade.append(CascadeLink(
            **{
                "from": f"Ambient Temperature ({scenario.temperature_c}°C)",
                "to": "Urban Heat Island Exposure",
                "evidence_status": "modeled",
                "intensity": round(heat_intensity, 2),
                "description": "High surface temperatures create thermal discomfort for outdoor workers (decoupled from flood chain)"
            }
        ))

    return cascade
