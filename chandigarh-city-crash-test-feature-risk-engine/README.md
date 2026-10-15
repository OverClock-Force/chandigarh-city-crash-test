# Chandigarh City Crash Test (C3T)

> *"Stress-test the city before reality does."*

An AI-powered urban stress testing and preventive decision intelligence platform for the digital public infrastructure of Chandigarh.

---

## 🎯 Executive Overview

Municipal challenges are conventionally managed in silos—waste collection, stormwater drainage, traffic advisories, and emergency response. However, urban failures cascade across domains:
- Rainfall + debris accumulation $\rightarrow$ clogged road gullies
- Reduced drainage capacity $\rightarrow$ surface waterlogging
- Waterlogged lanes $\rightarrow$ arterial traffic gridlock
- Traffic choke points $\rightarrow$ delayed emergency response

**C3T** flips traditional civic-tech:
Instead of asking *"Where is the current civic complaint?"*, C3T asks:  
**"What is likely to fail next, why will it fail, and which preventive action gives the city the best risk reduction per unit resource?"**

---

## 👥 Team Work Division & Ownership

| Member | Role | Owned Directory | Key Deliverables |
|---|---|---|---|
| **Aman Gairola** | Frontend & UI/UX Lead | `frontend/` | React/Vite/Tailwind dashboard with 6 screens: City Overview, Stress-Test Lab, Risk Analysis, Intervention Planner, Civic Reports, Methodology. |
| **Aman Gupta** | Backend & Data Lead | `backend/`, `data/`, `docs/api-contract.md` | FastAPI service, Pydantic schemas, REST endpoints, synthetic Chandigarh datasets, API contract coordination. |
| **Ankit Yadav** | Risk Engine & Logic Lead | `risk_engine/` | Rule-based scoring, causal cascade failure graph, constrained intervention optimizer. |
| **Aditya Raj** | AI Intake & QA Lead | `tests/`, `docs/demo-plan.md` | Test suite, integration validation, sample civic report corpus, hackathon demo flow. |

---

## ⚖️ The Golden Rule

> **Every simulated result is labeled illustrative / unvalidated.**  
> We never present it as an actual forecast for Chandigarh.  
> Every API response explicitly returns `data_status: "synthetic_demo"` and `score_label: "Unvalidated demo index (0-100)"`.

---

## 📂 Repository Structure

```
c3t-chandigarh-city-crash-test/
├── backend/                  # Aman Gupta: FastAPI service
│   ├── app/
│   │   ├── main.py           # FastAPI entrypoint with CORS & error handlers
│   │   ├── config.py         # Application settings
│   │   ├── routers/          # API route handlers
│   │   │   ├── health.py     # GET /health
│   │   │   ├── sectors.py    # GET /api/sectors
│   │   │   ├── events.py     # GET & POST /api/events
│   │   │   ├── stress_test.py# POST /api/stress-test
│   │   │   ├── optimize.py   # POST /api/optimize
│   │   │   └── scenarios.py  # GET & POST /api/scenarios
│   │   ├── schemas/          # Pydantic v2 schemas
│   │   └── storage/          # Thread-safe in-memory store & seeds
│   └── README.md
├── risk_engine/              # Ankit Yadav & Aman Gupta: Core logic package
│   ├── calculator.py         # Component & sector risk calculations
│   ├── cascade.py            # Failure chain generator (modeled/hypothetical)
│   ├── optimizer.py          # Constrained intervention optimizer
│   ├── models.py             # Scenario and intervention data models
│   └── tests/                # Direction-of-change and bounds unit tests
├── data/                     # Aman Gupta: Shared synthetic & calibrated data
│   ├── chandigarh_sectors.json
│   ├── chandigarh_sectors.geojson
│   ├── sample_civic_reports.json
│   └── default_scenarios.json
├── docs/                     # Shared specifications & contract
│   ├── api-contract.md       # Frozen API contract with examples
│   ├── data-provenance.md    # Source calibration & ethics notes
│   └── setup-guide.md        # Local environment setup instructions
├── tests/                    # Aditya Raj: Integration tests
│   ├── test_health_api.py
│   ├── test_sectors_api.py
│   ├── test_stress_test_api.py
│   ├── test_optimize_api.py
│   ├── test_events_api.py
│   └── test_scenarios_api.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Test Suite (15 passing tests)
```bash
python -m pytest tests risk_engine/tests -v
```

### 3. Launch the Backend Server
```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive API documentation will be available at:  
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)  
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## ⚡ Key API Endpoints

- `GET /health` - Health check & synthetic status
- `GET /api/sectors` - Chandigarh sectors with vulnerability attributes & GeoJSON
- `GET /api/events` · `POST /api/events` - Civic report intake & query
- `POST /api/stress-test` - Run scenario simulation & cascade graph
- `POST /api/optimize` - Compare candidate interventions under budget/team constraints
- `GET /api/scenarios` · `POST /api/scenarios` - Save & load stress scenarios
