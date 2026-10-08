"""AiSOC Backend — FastAPI application entry point."""
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
from app.services.simulator import start_simulator, stop_simulator
from app.services.network_monitor import start_network_monitor, stop_network_monitor

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", ".env.example"))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", ".env"), override=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    sim_task = asyncio.create_task(start_simulator(30, 50))
    net_task = asyncio.create_task(start_network_monitor(15))
    yield
    stop_simulator()
    stop_network_monitor()
    sim_task.cancel()
    net_task.cancel()

app = FastAPI(
    title="AiSOC API",
    description="AI-Driven Security Operations Center — Gen AI Capstone Project",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(alerts_router)
app.include_router(dashboard_router)
app.include_router(investigations_router)


@app.get("/")
async def root():
    return {"name": "AiSOC API", "version": "1.0.0", "status": "running",
            "project": "Gen AI Capstone Project — Group 4, PCCOE Pune",
            "monitors": ["network_monitor", "alert_simulator"]}

@app.get("/health")
async def health():
    return {"status": "healthy"}
