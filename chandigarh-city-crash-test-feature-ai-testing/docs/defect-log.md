# C3T Integration Defect Log & Known Limitations

**Milestone**: M3 Integration & M4 Polish  
**Lead Owner**: Aditya Raj (AI Intake, QA & Demo Lead)  
**Status**: All Critical Integration Defects Resolved

---

## 🐞 Defect Resolution Log

| ID | Component | Description | Root Cause | Resolution | Status |
|---|---|---|---|---|---|
| **DEF-001** | Git Config | Git untracked bytecode & `.venv` causing missing file perception. | `.gitignore` only had `node_modules`. Switching branches left `.pyc` files unlinked. | Updated `.gitignore` with Python bytecode, caches, `.venv`, `dist`, and `.env` rules. Cleanly restored source from `feature/backend-api`. | **RESOLVED** |
| **DEF-002** | Frontend API Client | `runStressTest()` sent frontend field names (`rainfall`, `debris`) instead of backend contract (`rainfall_mm`, `debris_level`). | Missing payload mapper between React UI form state and Pydantic schema. | Added `formatScenarioPayload()` in `src/api/client.js` with comprehensive categorical and numeric transforms. | **RESOLVED** |
| **DEF-003** | Frontend API Client | `getSectors()` expected array; backend returned `{ sectors: [...] }`. | Response envelope shape mismatch. | Updated `src/App.jsx` to unpack `data.sectors` with graceful fallback. | **RESOLVED** |
| **DEF-004** | Frontend API Client | `getEvents()` expected array; backend returned `{ events: [...] }`. | Response envelope shape mismatch. | Updated `src/App.jsx` to unpack `data.events` and format sector labels. | **RESOLVED** |
| **DEF-005** | Intervention Planner | Intervention Planner screen used static placeholder values instead of backend `/api/optimize`. | Optimizer endpoint had not been connected to the UI in initial prototype. | Wired `optimizeInterventions()` to `src/App.jsx` Screen 04, rendering real candidate evaluations, utility, and resource usage. | **RESOLVED** |
| **DEF-006** | Risk Analysis Screen | Failure cascade graph was static in UI. | Simulation cascade payload was not rendered dynamically in Screen 03. | Connected `apiResult.cascade` to Screen 03, visualizing transfer intensities and `modeled` / `hypothetical` evidence badges. | **RESOLVED** |
| **DEF-007** | Civic Reports Screen | Citizen incident submission was session-only. | Form submission was not dispatched to backend `/api/events`. | Added `submitCivicReport()` in API client and wired form submission to persist to backend thread-safe data store. | **RESOLVED** |

---

## ⚠️ Known Limitations & Future Work (Section 10)

1. **Synthetic Spatial Data**:
   - Sector boundaries and coordinates are synthetic representations of Chandigarh Sectors 17, 22, 35, 43, 26, 8, 9, 19, 15, and Industrial Area Phase 1.
   - Future work: Ingest official GIS shapefiles from Chandigarh Master Plan 2031 upon licensing approval.
2. **Deterministic Heuristic Scoring**:
   - Risk scoring uses empirical hydraulic and traffic weights rather than numerical hydro-dynamic 2D flood simulation (e.g., SWMM or TUFLOW).
   - Future work: Calibrate weights against actual monsoon rainfall sensor telemetry.
3. **In-Memory Thread-Safe Storage**:
   - Backend persists reports and custom scenarios in an in-memory thread-safe store (`DataStore`).
   - Future work: Connect to PostgreSQL / PostGIS database for durable multi-year spatial queries.
4. **Decoupled Heat Stress**:
   - Ambient temperature ($32^\circ\text{C}$ to $43^\circ\text{C}$) is tracked as an independent environmental vulnerability pathway and does not alter flood inundation scores.
