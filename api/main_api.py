"""
Vedic Career Prediction API – FastAPI entrypoint.
Run from project root: uvicorn api.main_api:app --host 0.0.0.0 --port 8000
"""
import os
import sys

# Ensure project root is on path when running as uvicorn api.main_api:app
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
os.chdir(_ROOT)

try:
    import environment_config  # noqa: F401 - loads env for Supabase, Google, etc.
except Exception:
    pass
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import charts
from api.routes import ashtavargam_routes
from api.routes import career
from api.routes import prediction
from api.routes import dasha_routes

app = FastAPI(
    title="Vedic Career Prediction API",
    description="Deterministic D1/D10 charts, career rules, Dasha, BAV/SAV integration",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(charts.router)
app.include_router(ashtavargam_routes.router)
app.include_router(career.router)
app.include_router(prediction.router)
app.include_router(dasha_routes.router)


@app.get("/health")
def health():
    """Health check for agents and load balancers."""
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
