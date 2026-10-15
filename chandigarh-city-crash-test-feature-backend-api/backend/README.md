# C3T Backend Service

Owner: **Aman Gupta (Backend & Data Lead)**

This service powers the Chandigarh City Crash Test (C3T) platform, providing high-performance FastAPI endpoints for scenario stress-testing, risk breakdown calculations, causal cascade graphs, and resource-constrained intervention optimization.

---

## Architecture Principles

1. **Separation of Concerns**: Route handlers in `backend/app/routers/` do not contain business risk logic. All modeling logic lives cleanly in the importable `risk_engine` package.
2. **Contract-First Design**: Fully typed Pydantic v2 schemas adhering strictly to `docs/api-contract.md`.
3. **Mandatory Illustrative Labeling**: All outputs return `data_status: "synthetic_demo"` and `score_label: "Unvalidated demo index (0-100)"`.
4. **CORS Configured**: Ready to connect with Aman Gairola's React/Vite frontend on `http://localhost:3000` or `http://localhost:5173`.

---

## Running Locally

```bash
# Start server with auto-reload
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive Docs:
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Testing

```bash
python -m pytest tests/ -v
```
