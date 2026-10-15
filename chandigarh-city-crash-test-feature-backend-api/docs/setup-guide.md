# C3T Setup & Developer Guide

## 1. Prerequisites
- **Python**: 3.10+ (tested on Python 3.12 / 3.15)
- **Node.js**: 18+ (for frontend repository integration)
- **Git**

---

## 2. Quickstart: Backend Service

### Step 1: Clone and Enter Repository
```bash
git clone <repo-url>
cd c3t-chandigarh-city-crash-test
```

### Step 2: Set Up Python Virtual Environment (Recommended)
```bash
python -m venv env
# On Windows:
.\env\Scripts\activate
# On Linux/macOS:
source env/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run Tests
```bash
python -m pytest tests risk_engine/tests -v
```
All 15 tests should pass.

### Step 5: Start the Backend Server
```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
The interactive Swagger API documentation will be available at:  
👉 **http://localhost:8000/docs**  
ReDoc is available at:  
👉 **http://localhost:8000/redoc**

---

## 3. Verifying Key Endpoints

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Sectors & GeoJSON
```bash
curl http://localhost:8000/api/sectors
```

### 3. Run Benchmark 60mm Stress Test
```bash
curl -X POST http://localhost:8000/api/stress-test \
  -H "Content-Type: application/json" \
  -d '{
    "rainfall_mm": 60,
    "debris_level": "high",
    "drain_condition": "partial_blockage",
    "traffic_level": "peak",
    "temperature_c": 38,
    "resources": { "maintenance_teams": 4, "pumping_units": 2, "budget_inr": 350000 }
  }'
```

### 4. Run Intervention Optimizer
```bash
curl -X POST http://localhost:8000/api/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "rainfall_mm": 60,
    "debris_level": "high",
    "drain_condition": "partial_blockage",
    "traffic_level": "peak",
    "temperature_c": 38,
    "resources": { "maintenance_teams": 4, "pumping_units": 2, "budget_inr": 350000 }
  }'
```

---

## 4. Frontend Integration Notes for Aman Gairola

- The FastAPI server enables CORS for `http://localhost:3000` and `http://localhost:5173`.
- All requests adhere directly to the schemas defined in `docs/api-contract.md`.
- Default scenario IDs (`scen-default-60mm`, `scen-cloudburst-100mm`, etc.) can be retrieved via `GET /api/scenarios`.
