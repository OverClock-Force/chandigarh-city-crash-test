# C3T API Contract Specification

**Project**: Chandigarh City Crash Test (C3T)  
**Version**: 1.0.0  
**Owner**: Aman Gupta (Backend & Data Lead)  
**Collaborators**: Aman Gairola (Frontend Lead), Ankit Yadav (Risk Engine Lead), Aditya Raj (QA & Demo Lead)  
**Status**: Agreed & Frozen (Milestone Gate)

---

## 1. Global Principles & Data Labeling

> **Golden Rule**: Every simulated result is labeled **illustrative / unvalidated**. We never present it as a real forecast for Chandigarh.

Every response payload providing risk metrics or sector data carries two mandatory metadata fields:
- `data_status`: `"synthetic_demo"`
- `score_label`: `"Unvalidated demo index (0-100)"`

The Frontend UI must render these badges whenever displaying simulation outcomes.

---

## 2. Endpoints Overview

| Method | Endpoint | Description | Status |
|---|---|---|---|
| `GET` | `/health` | Service health check | Implemented |
| `GET` | `/api/sectors` | Chandigarh sectors, attributes, and GeoJSON boundaries | Implemented |
| `GET` | `/api/events` | List citizen & field civic reports (optional `?sector_id=`) | Implemented |
| `POST` | `/api/events` | Submit a new civic report / incident | Implemented |
| `POST` | `/api/stress-test` | Run scenario simulation, risk scoring, & cascade graph | Implemented |
| `POST` | `/api/optimize` | Constrained intervention comparison against Do Nothing baseline | Implemented |
| `GET` | `/api/scenarios` | List saved baseline and benchmark scenarios | Implemented |
| `POST` | `/api/scenarios` | Save a custom scenario configuration | Implemented |
| `GET` | `/api/scenarios/{id}`| Retrieve a saved scenario by ID | Implemented |

---

## 3. Input Validation Rules

The UI and Backend enforce these exact rules:

| Field | Type | Allowed Values / Range | Description |
|---|---|---|---|
| `rainfall_mm` | Float | `15.0` to `100.0` | Total rainfall in mm. |
| `rainfall_duration_hours`| Float / null | `0.1` to `48.0` or `null` | Optional duration. Cloudburst vs prolonged rain. |
| `debris_level` | String | `"normal"`, `"high"`, `"extreme"` | Solid waste & leaf litter loading. |
| `drain_condition` | String | `"good"`, `"partial_blockage"`, `"critical"` | Baseline drainage infrastructure condition. |
| `traffic_level` | String | `"normal"`, `"peak"` | Citywide road congestion baseline. |
| `temperature_c` | Float | `32.0` to `43.0` | Treated as an independent heat-stress pathway; **does not** raise flood risk. |
| `resources` | Object | Object with counts/budget | Inventory available for preventive action. |
| `resources.maintenance_teams` | Integer | `>= 0` (default 4) | Available municipal field crews. |
| `resources.pumping_units` | Integer | `>= 0` (default 2) | Available mobile high-capacity pumps. |
| `resources.budget_inr` | Float | `>= 0.0` (default 350,000) | Available emergency contingency budget. |

---

## 4. Endpoint Specifications

### 4.1 Health Check
**`GET /health`**

Response:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "service": "C3T Chandigarh City Crash Test API",
  "data_status": "synthetic_demo",
  "message": "Backend active. Decision intelligence engine online."
}
```

---

### 4.2 Sectors and Spatial Data
**`GET /api/sectors`**

Response:
```json
{
  "data_status": "synthetic_demo",
  "score_label": "Unvalidated demo index (0-100)",
  "total_sectors": 10,
  "sectors": [
    {
      "sector_id": "sector-17",
      "name": "Sector 17 (City Center & Plaza)",
      "elevation_factor": 0.85,
      "drain_vulnerability": 0.80,
      "road_exposure": 0.90,
      "waste_pressure": 0.75,
      "green_cover_factor": 0.35,
      "is_historic_hotspot": true,
      "critical_infrastructure": [
        "ISBT Sector 17",
        "Municipal Corporation HQ",
        "Sector 17 Underpass"
      ],
      "coordinates": { "lat": 30.7398, "lng": 76.7827 }
    }
  ],
  "geojson": {
    "type": "FeatureCollection",
    "features": [...]
  }
}
```

---

### 4.3 Stress-Test Simulation
**`POST /api/stress-test`**

Request:
```json
{
  "rainfall_mm": 60.0,
  "rainfall_duration_hours": null,
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
```

Response:
```json
{
  "scenario_id": "scen-f8a912b3",
  "data_status": "synthetic_demo",
  "score_label": "Unvalidated demo index (0-100)",
  "overall_score": 67.4,
  "components": {
    "drainage_stress": 67.1,
    "waterlogging": 69.4,
    "road_traffic": 76.2,
    "emergency_access": 73.5,
    "heat_stress_context": 54.5
  },
  "sectors": [
    {
      "sector_id": "sector-17",
      "sector_name": "Sector 17 (City Center & Plaza)",
      "score": 88.5,
      "category": "severe",
      "main_factors": [
        "Documented recurring monsoon waterlogging hotspot (Chandigarh MC 2026)",
        "High storm-drain vulnerability & gully blockage susceptibility (partial_blockage)",
        "Low-lying topographic depression prone to surface runoff pooling"
      ]
    }
  ],
  "cascade": [
    {
      "from": "Rainfall (60.0mm)",
      "to": "Drainage System Stress",
      "evidence_status": "modeled",
      "intensity": 0.6,
      "description": "Precipitation volume (60.0mm) approaches or exceeds stormwater carrying capacity"
    },
    {
      "from": "Drainage System Stress",
      "to": "Surface Waterlogging Hotspots",
      "evidence_status": "modeled",
      "intensity": 0.67,
      "description": "Uncollected stormwater backs up onto carriageways and roundabouts"
    },
    {
      "from": "Surface Waterlogging Hotspots",
      "to": "Road Traffic Disruption",
      "evidence_status": "modeled",
      "intensity": 0.62,
      "description": "Flooded lane sections throttle vehicle speeds (peak traffic baseline)"
    },
    {
      "from": "Road Traffic Disruption",
      "to": "Emergency Response Access Delay",
      "evidence_status": "hypothetical",
      "intensity": 0.65,
      "description": "Ambulance and fire corridor transit times degrade due to arterial choke points"
    }
  ],
  "assumptions": [
    "Unvalidated heuristic model for hackathon decision exploration only.",
    "Rainfall runoff response assumes standard Chandigarh urban impervious surface ratio (~65-75%).",
    "Temperature is computed as an independent heat-stress pathway and intentionally decoupled from flood mechanics."
  ]
}
```

---

### 4.4 Intervention Optimizer
**`POST /api/optimize`**

Request: Same format as `POST /api/stress-test`.

Response:
```json
{
  "data_status": "synthetic_demo",
  "score_label": "Unvalidated demo index (0-100)",
  "baseline_score": 67.4,
  "recommended_action": {
    "action_id": "clear_gullies_and_reroute",
    "name": "Clear Priority Gullies + Reroute Traffic",
    "is_feasible": true,
    "feasibility_reasons": ["Feasible within current resource constraints."],
    "resources_used": {
      "maintenance_teams": 3,
      "pumping_units": 0,
      "budget_inr": 60000.0
    },
    "resources_remaining": {
      "maintenance_teams": 1,
      "pumping_units": 2,
      "budget_inr": 290000.0
    },
    "baseline_risk_score": 67.4,
    "modeled_risk_score": 46.8,
    "risk_reduction": 20.6,
    "utility_score": 12.8,
    "assumptions": [
      "Evaluated with identical risk engine logic for intervention 'Clear Priority Gullies + Reroute Traffic'."
    ],
    "components": {
      "drainage_stress": 52.3,
      "waterlogging": 48.7,
      "road_traffic": 38.5,
      "emergency_access": 42.6,
      "heat_stress_context": 54.5
    }
  },
  "all_evaluations": [
    {
      "action_id": "do_nothing",
      "name": "Do Nothing (Unmitigated Baseline)",
      "is_feasible": true,
      "modeled_risk_score": 67.4,
      "risk_reduction": 0.0,
      "utility_score": 0.0
    },
    ...
  ],
  "comparison_summary": "Recommended 'Clear Priority Gullies + Reroute Traffic'. Achieves highest utility..."
}
```

---

### 4.5 Civic Reports
**`GET /api/events`** (Query param: `?sector_id=sector-17`)
**`POST /api/events`**

Post Body:
```json
{
  "category": "drainage_blockage",
  "severity": "high",
  "sector_id": "sector-17",
  "location_description": "Road gully grating choked near Plaza fountain",
  "source": "citizen_mobile",
  "confidence": 0.95
}
```

---

### 4.6 Scenarios
**`GET /api/scenarios`**
**`POST /api/scenarios`**
**`GET /api/scenarios/{id}`**

Lists pre-seeded benchmarks (`scen-default-60mm`, `scen-cloudburst-100mm`, etc.) and allows saving customized runs.
