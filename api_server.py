"""ACPIA API server — connects the dashboard (dashboard.html) to the agent pipeline.

Run with:
    pip install fastapi "uvicorn[standard]"
    uvicorn api_server:app --reload --port 8000

Endpoints:
    POST /api/cases   submit a new complaint; runs the full 4-agent pipeline
                      synchronously and returns the complete result
    GET  /api/cases   list every case processed since the server started
    GET  /api/health  simple liveness check
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from pipeline import run_pipeline

app = FastAPI(title="ACPIA API")

_DASHBOARD_PATH = os.path.join(os.path.dirname(__file__), "dashboard.html")


@app.get("/")
async def serve_dashboard():
    """Serves the dashboard itself, so visiting http://localhost:8000 just works."""
    return FileResponse(_DASHBOARD_PATH)

# Dashboard is opened as a local static file / dev server, so allow any origin
# for this demo. Restrict this before putting real complaints through it.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory case store for the demo. Swap for Postgres (see database/ folder
# in the brief) to persist across restarts.
_cases_store: list[dict] = []


class ComplaintRequest(BaseModel):
    complaint_text: str


@app.post("/api/cases")
async def submit_complaint(payload: ComplaintRequest):
    result = await run_pipeline(payload.complaint_text)
    result["case_number"] = len(_cases_store) + 1
    _cases_store.append(result)
    return result


@app.get("/api/cases")
async def list_cases():
    return list(reversed(_cases_store))  # newest first


@app.get("/api/health")
async def health():
    return {"status": "ok"}