# Data Provenance & Ethics Specification

**Project**: Chandigarh City Crash Test (C3T)  
**Dataset Version**: 1.0.0-synthetic-demo  
**Status**: Synthetic Prototype Calibration  

---

## 1. Summary of Data Sources & Provenance

| Dataset Asset | Real vs Synthetic | Primary Source / Basis | License / Usage | Role in C3T |
|---|---|---|---|---|
| **Chandigarh Sector Topography & Layout** | Real-derived context | Survey of India / Chandigarh Open Spatial Data | Open Government Data (OGD) India | Spatial boundaries, sector center coordinates, road corridors |
| **Monsoon Waterlogging Hotspots** | Real administrative signal | Chandigarh Municipal Corporation (MC) 2026 Surveys (52 hotspots mapped in Aug 2026; 23 staged in Jul 2026) | Public Press & Administrative Releases (Times of India / Chandigarh MC) | Hotspot flags for Sector 17 underpass, Sector 22 Aroma chowk, Sector 35 roundabout, Sector 43 ISBT, Sector 26 Mandi |
| **Drain Infrastructure & Gully Status** | Calibrated synthetic | Heuristic mapping based on historic siltation reports | Synthetic Demo Data | Categorical status (`good`, `partial_blockage`, `critical`) |
| **Debris & Waste Pressure** | Calibrated synthetic | Chandigarh Smart City / Swachh Bharat market waste density estimates | Synthetic Demo Data | Waste pressure coefficient per sector (`normal`, `high`, `extreme`) |
| **Municipal Resources & Inventory** | Synthetic | Fictional operational staging (crews, suction pumps, INR budgets) | Synthetic Demo Data | Resource constraints for Intervention Optimizer |
| **Civic Reports Stream** | Synthetic | Simulated citizen mobile and surveillance event reports | Synthetic Demo Data | Event ingestion test data (`/api/events`) |

---

## 2. Responsible AI & Governance Rules

1. **Mandatory Illustrative Labeling**:
   - Every API output carries `"data_status": "synthetic_demo"` and `"score_label": "Unvalidated demo index (0-100)"`.
   - The UI is strictly forbidden from displaying risk scores without the accompanying caveat badge.
2. **Advisory Decision Support Only**:
   - C3T is designed as decision support intelligence for municipal planners, not an autonomous authority.
   - High-impact operational dispatches require human authorization.
3. **Privacy & Data Minimization**:
   - Civic event reports store no Personally Identifiable Information (PII).
   - Citizen complaints are aggregated at the sector/node level without personal tracking.
4. **Causal Transparency**:
   - All cascade graph edges explicitly distinguish between `"modeled"` and `"hypothetical"` links.
   - Black-box composite scores are always broken down into explainable contributing factors.

---

## 3. Known Limitations

- **Topographic Resolution**: The prototype uses sector-level aggregate elevation factors rather than high-resolution LiDAR Digital Elevation Models (DEM).
- **Hydrological Simplification**: A lightweight predictive surrogate heuristic is used instead of computational fluid dynamics (CFD) hydrodynamic simulations (such as SWMM or 2D overland flow).
- **Static Resource Transit**: Field intervention crews and pumping units are assumed to arrive within pre-storm staging windows without simulated traffic routing transit delays.
