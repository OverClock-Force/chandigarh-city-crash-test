from typing import List, Dict, Any, Tuple
import copy
from .models import (
    ScenarioInput,
    SectorData,
    InterventionEvaluation,
    OptimizationResult,
    ComponentScores,
)
from .calculator import calculate_scenario_risk, compute_component_scores


# Pre-defined candidate intervention packages from C3T specification
DEFAULT_INTERVENTIONS = [
    {
        "action_id": "do_nothing",
        "name": "Do Nothing (Unmitigated Baseline)",
        "description": "Maintain status quo with no preventive field action taken before storm onset.",
        "maintenance_teams_needed": 0,
        "pumping_units_needed": 0,
        "cost_inr": 0.0,
        "operational_burden_score": 0.0,
        "effect": "none"
    },
    {
        "action_id": "clear_priority_gullies",
        "name": "Clear Priority Road Gullies",
        "description": "Pre-storm desilting and clearing of grates across major waterlogging corridors (e.g., Madhya Marg & Sector 17).",
        "maintenance_teams_needed": 2,
        "pumping_units_needed": 0,
        "cost_inr": 45000.0,
        "operational_burden_score": 25.0,
        "effect": "improve_drain"
    },
    {
        "action_id": "remove_waste_hotspots",
        "name": "Remove Waste / Debris Hotspots",
        "description": "Clear solid waste heaps and loose commercial garbage near municipal stormwater catch basins.",
        "maintenance_teams_needed": 2,
        "pumping_units_needed": 0,
        "cost_inr": 60000.0,
        "operational_burden_score": 30.0,
        "effect": "reduce_debris"
    },
    {
        "action_id": "deploy_suction_pumps",
        "name": "Deploy Suction / Pumping Units",
        "description": "Position high-capacity diesel pumping units at critical low-lying roundabouts and underpasses.",
        "maintenance_teams_needed": 1,
        "pumping_units_needed": 2,
        "cost_inr": 120000.0,
        "operational_burden_score": 45.0,
        "effect": "deploy_pumps"
    },
    {
        "action_id": "reroute_traffic",
        "name": "Temporary Traffic Rerouting",
        "description": "Deploy traffic marshals and digital signboards to divert arterial flow away from flood-prone intersections.",
        "maintenance_teams_needed": 1,
        "pumping_units_needed": 0,
        "cost_inr": 15000.0,
        "operational_burden_score": 15.0,
        "effect": "mitigate_traffic"
    },
    {
        "action_id": "clear_gullies_and_reroute",
        "name": "Clear Priority Gullies + Reroute Traffic",
        "description": "Dual intervention combining proactive gully desilting with proactive arterial traffic diversion.",
        "maintenance_teams_needed": 3,
        "pumping_units_needed": 0,
        "cost_inr": 60000.0,
        "operational_burden_score": 35.0,
        "effect": "clear_and_reroute"
    },
    {
        "action_id": "full_synergistic_response",
        "name": "Full Emergency Response (Gullies + Pumps + Traffic)",
        "description": "Maximal city mobilization deploying gully crews, mobile pumping units, and active traffic diversion.",
        "maintenance_teams_needed": 4,
        "pumping_units_needed": 2,
        "cost_inr": 180000.0,
        "operational_burden_score": 70.0,
        "effect": "full_protocol"
    }
]


def apply_intervention_to_scenario(scenario: ScenarioInput, effect: str) -> ScenarioInput:
    """
    Creates a deep copy of scenario and applies the physical transformation of the intervention.
    """
    scen_copy = copy.deepcopy(scenario)

    if effect == "none":
        pass
    elif effect == "improve_drain":
        # Upgrades drain condition by one grade
        if scen_copy.drain_condition == "critical":
            scen_copy.drain_condition = "partial_blockage"
        elif scen_copy.drain_condition == "partial_blockage":
            scen_copy.drain_condition = "good"
    elif effect == "reduce_debris":
        # Lowers debris load
        if scen_copy.debris_level == "extreme":
            scen_copy.debris_level = "high"
        elif scen_copy.debris_level == "high":
            scen_copy.debris_level = "normal"
    elif effect == "deploy_pumps":
        # Pumping units offset effective rainfall retention by 20mm
        scen_copy.rainfall_mm = max(15.0, scen_copy.rainfall_mm - 20.0)
    elif effect == "mitigate_traffic":
        if scen_copy.traffic_level == "peak":
            scen_copy.traffic_level = "normal"
    elif effect == "clear_and_reroute":
        # Drain upgrade + traffic reroute
        if scen_copy.drain_condition == "critical":
            scen_copy.drain_condition = "partial_blockage"
        elif scen_copy.drain_condition == "partial_blockage":
            scen_copy.drain_condition = "good"
        if scen_copy.traffic_level == "peak":
            scen_copy.traffic_level = "normal"
    elif effect == "full_protocol":
        # Full protocol
        if scen_copy.drain_condition == "critical":
            scen_copy.drain_condition = "partial_blockage"
        elif scen_copy.drain_condition == "partial_blockage":
            scen_copy.drain_condition = "good"
        if scen_copy.debris_level == "extreme":
            scen_copy.debris_level = "high"
        elif scen_copy.debris_level == "high":
            scen_copy.debris_level = "normal"
        if scen_copy.traffic_level == "peak":
            scen_copy.traffic_level = "normal"
        scen_copy.rainfall_mm = max(15.0, scen_copy.rainfall_mm - 20.0)

    return scen_copy


def evaluate_interventions(
    scenario: ScenarioInput,
    sectors_data: List[SectorData],
    candidate_list: List[Dict[str, Any]] = None
) -> OptimizationResult:
    """
    Evaluates candidate interventions against baseline, checks resource bounds,
    re-runs the identical risk engine on modified scenario copies, and calculates
    constrained utility:
        Utility = risk_reduction - (lambda * cost) - (mu * operational_burden)
    """
    if candidate_list is None:
        candidate_list = DEFAULT_INTERVENTIONS

    # 1. Calculate baseline
    baseline_result = calculate_scenario_risk(scenario, sectors_data)
    baseline_score = baseline_result.overall_score

    available_teams = scenario.resources.maintenance_teams
    available_pumps = scenario.resources.pumping_units
    available_budget = scenario.resources.budget_inr

    # Utility penalization coefficients (tuned for INR / score balancing)
    LAMBDA_COST = 0.00006  # 50k INR cost = ~3.0 utility points penalty
    MU_BURDEN = 0.12       # 25 burden = 3.0 points penalty

    evaluations: List[InterventionEvaluation] = []

    for item in candidate_list:
        needed_teams = item["maintenance_teams_needed"]
        needed_pumps = item["pumping_units_needed"]
        cost = item["cost_inr"]
        burden = item["operational_burden_score"]

        # Resource Feasibility Check
        reasons = []
        is_feasible = True

        if needed_teams > available_teams:
            is_feasible = False
            reasons.append(f"Insufficient maintenance teams: needs {needed_teams}, only {available_teams} available")
        if needed_pumps > available_pumps:
            is_feasible = False
            reasons.append(f"Insufficient pumping units: needs {needed_pumps}, only {available_pumps} available")
        if cost > available_budget:
            is_feasible = False
            reasons.append(f"Exceeds allocated budget: needs ₹{cost:,.0f}, budget is ₹{available_budget:,.0f}")

        resources_used = {
            "maintenance_teams": needed_teams if is_feasible else 0,
            "pumping_units": needed_pumps if is_feasible else 0,
            "budget_inr": cost if is_feasible else 0.0,
        }
        resources_remaining = {
            "maintenance_teams": max(0, available_teams - needed_teams),
            "pumping_units": max(0, available_pumps - needed_pumps),
            "budget_inr": max(0.0, available_budget - cost),
        }

        # Apply intervention & re-run exact same engine
        modified_scenario = apply_intervention_to_scenario(scenario, item["effect"])
        sim_result = calculate_scenario_risk(modified_scenario, sectors_data)
        modeled_risk = sim_result.overall_score

        risk_reduction = round(max(0.0, baseline_score - modeled_risk), 1)

        # Constrained utility
        if is_feasible:
            raw_utility = risk_reduction - (LAMBDA_COST * cost) - (MU_BURDEN * burden)
            utility_score = round(raw_utility, 2)
            if not reasons:
                reasons.append("Feasible within current resource constraints.")
        else:
            utility_score = -999.0  # Infeasible actions penalized

        assumptions = [
            f"Evaluated with identical risk engine logic for intervention '{item['name']}'.",
            f"Assumes field teams achieve intended mitigation within lead time before storm peak."
        ]

        evaluations.append(InterventionEvaluation(
            action_id=item["action_id"],
            name=item["name"],
            is_feasible=is_feasible,
            feasibility_reasons=reasons,
            resources_used=resources_used,
            resources_remaining=resources_remaining,
            baseline_risk_score=baseline_score,
            modeled_risk_score=modeled_risk,
            risk_reduction=risk_reduction,
            utility_score=utility_score,
            assumptions=assumptions,
            components=sim_result.components
        ))

    # Determine recommended action:
    # Best feasible action with highest utility score
    feasible_evals = [e for e in evaluations if e.is_feasible and e.action_id != "do_nothing"]
    if feasible_evals:
        # Sort by highest utility score
        feasible_evals.sort(key=lambda e: (e.utility_score, e.risk_reduction), reverse=True)
        recommended = feasible_evals[0]
        summary = (
            f"Recommended '{recommended.name}'. Achieves highest utility ({recommended.utility_score}) "
            f"with {recommended.risk_reduction} pt risk reduction (from {baseline_score} to {recommended.modeled_risk_score}), "
            f"leaving {recommended.resources_remaining['maintenance_teams']} teams, "
            f"{recommended.resources_remaining['pumping_units']} pumps, and "
            f"₹{recommended.resources_remaining['budget_inr']:,.0f} budget remaining."
        )
    else:
        # Fallback to do_nothing
        recommended = [e for e in evaluations if e.action_id == "do_nothing"][0]
        summary = "No non-baseline intervention was feasible under the provided resource constraints. Baseline 'Do Nothing' retained."

    return OptimizationResult(
        data_status="synthetic_demo",
        score_label="Unvalidated demo index (0-100)",
        baseline_score=baseline_score,
        recommended_action=recommended,
        all_evaluations=evaluations,
        comparison_summary=summary
    )


def optimize_interventions(
    scenario: ScenarioInput,
    sectors_data: List[SectorData]
) -> OptimizationResult:
    return evaluate_interventions(scenario, sectors_data)
