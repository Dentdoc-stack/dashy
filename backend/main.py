"""
main.py — FastAPI application entry point.
KP-HCIP Multi-Package Executive Dashboard API
"""

import sys
import os
import logging

# Add project root to sys.path so root-level modules (config, loader, transform) are importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.data_store import store
from backend.routers.data_router import router as data_router
from backend.routers.filters_router import router as filters_router
from backend.routers.package_router import router as package_router
from backend.routers.site_router import router as site_router
from backend.routers.situation_room_router import router as situation_room_router
from backend.routers.risk_router import router as risk_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: load data; Shutdown: nothing special."""
    logger.info("Loading data on startup...")
    warnings = store.load(force_refresh=False)
    for w in warnings:
        logger.info("  %s", w)
    logger.info("Data loaded. df_tasks=%d rows, df_site=%d rows",
                len(store.df_tasks), len(store.df_site))
    yield


app = FastAPI(
    title="KP-HCIP Dashboard API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(data_router, prefix="/api/data", tags=["Data"])
app.include_router(filters_router, prefix="/api/filters", tags=["Filters"])
app.include_router(package_router, prefix="/api/packages", tags=["Packages"])
app.include_router(site_router, prefix="/api/sites", tags=["Sites"])
app.include_router(situation_room_router, prefix="/api/situation-room", tags=["Situation Room"])
app.include_router(risk_router, prefix="/api/risk", tags=["Risk"])


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "rows_tasks": len(store.df_tasks),
        "rows_sites": len(store.df_site),
        "cache_timestamp": store.cache_timestamp,
    }
