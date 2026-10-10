"""AiSOC Backend — FastAPI entry point.

Starts three background services:
1. Alert Simulator — generates synthetic alerts
2. Network Monitor — scans real network traffic
3. Correlation Engine — groups related alerts
"""
import os
import asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routes.alerts import router as alerts_router
from app.routes.dashboard import router as dashboard_router
from app.routes.investigations import router as investigations_router
from app.routes.demo import router as demo_router
from app.services.simulator import start_simulator, stop_simulator
from app.services.network_monitor import start_network_monitor, stop_network_monitor
from app.services.correlation import start_correlation_engine, stop_correlation_engine

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", ".env.example"))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", ".env"), override=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    tasks = [
        asyncio.create_task(start_simulator(30, 50)),
        asyncio.create_task(start_network_monitor(15)),
        asyncio.create_task(start_correlation_engine(60)),
    ]
    yield
    stop_simulator()
    stop_network_monitor()
    stop_correlation_engine()
    for t in tasks:
        t.cancel()

app = FastAPI(
    title="AiSOC API",
    description="AI-Driven Security Operations Center — Gen AI Capstone Project, Group 4, PCCOE",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo (phone access)
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

app.include_router(alerts_router)
app.include_router(dashboard_router)
app.include_router(investigations_router)
app.include_router(demo_router)

@app.get("/")
async def root():
    return {"name": "AiSOC API", "version": "1.0.0", "status": "running",
            "project": "Gen AI Capstone — Group 4, PCCOE Pune",
            "services": ["simulator", "network_monitor", "correlation_engine"],
            "features": ["ocsf_normalization", "pseudonymization", "sha256_ledger",
                         "multi_agent_pipeline", "alert_correlation"],
            "demo": "Open /demo on your phone to trigger live alerts"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
