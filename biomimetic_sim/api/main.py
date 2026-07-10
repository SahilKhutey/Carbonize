"""
api/main.py
FastAPI application entry point.
Initializes middleware, routers, and DB engine lifespan managers.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.connection import engine
from database.models import Base
from api.routes import plants, simulations, reports

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to handle startup/shutdown tasks."""
    # Ensure database schemas are fully created on application launch
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown logic if any (close connection pools)
    await engine.dispose()

app = FastAPI(
    title="Biomimetic Industrial Simulation Platform",
    description="Full-stack simulation engine for biomineralization carbon capture retrofit grids.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register endpoints
app.include_router(plants.router, prefix="/api")
app.include_router(simulations.router, prefix="/api")
app.include_router(reports.router, prefix="/api")

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for container/orchestrator liveliness checks."""
    return {"status": "healthy", "service": "biomimetic-sim-api"}
