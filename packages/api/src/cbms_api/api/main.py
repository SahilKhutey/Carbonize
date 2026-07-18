"""
api/main.py
FastAPI application entry point.
Initializes middleware, routers, and DB engine lifespan managers.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from cbms_api.database.connection import engine, init_database_rls
from cbms_api.database.models import Base
from cbms_api.api.routes import auth, plants, simulations, reports, reagents, analytics, operator
from cbms_api.middleware.tenant_isolation import TenantIsolationMiddleware
from fastapi.responses import JSONResponse
from cbms_shared.exceptions import (
    AuthenticationError, AuthorizationError, NotFoundError,
    ValidationFailedError, RateLimitError
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to handle startup/shutdown tasks."""
    # Ensure database schemas are fully created on application launch
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Initialize RLS policies
    await init_database_rls()
    yield
    # Shutdown logic if any (close connection pools)
    await engine.dispose()

app = FastAPI(
    title="Biomimetic Industrial Simulation Platform",
    description="Full-stack simulation engine for biomineralization carbon capture retrofit grids.",
    version="1.0.0",
    lifespan=lifespan
)

from cbms_api.middleware.request_size_limit import RequestSizeLimitMiddleware
from cbms_api.middleware.timeout import TimeoutMiddleware
from cbms_api.middleware.rate_limiting import limiter, rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Enable CORS for frontend interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enable Request Size Limit
app.add_middleware(RequestSizeLimitMiddleware, default_max_mb=1.0)

# Enable Request Timeout
app.add_middleware(TimeoutMiddleware, default_timeout=30.0)

# Enable Rate Limiting (SlowAPI)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Enable Tenant Isolation (scopes DB session contexts, innermost)
app.add_middleware(TenantIsolationMiddleware)

# Exception handlers for clean API responses
@app.exception_handler(AuthenticationError)
async def authentication_error_handler(request, exc):
    return JSONResponse(
        status_code=401,
        content={"detail": exc.message if hasattr(exc, "message") else str(exc)}
    )

@app.exception_handler(AuthorizationError)
async def authorization_error_handler(request, exc):
    return JSONResponse(
        status_code=403,
        content={"detail": exc.message if hasattr(exc, "message") else str(exc)}
    )

@app.exception_handler(NotFoundError)
async def not_found_error_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": exc.message if hasattr(exc, "message") else str(exc)}
    )

@app.exception_handler(ValidationFailedError)
async def validation_failed_error_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.message if hasattr(exc, "message") else str(exc)}
    )

@app.exception_handler(RateLimitError)
async def rate_limit_error_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": exc.message if hasattr(exc, "message") else str(exc)}
    )

# Register endpoints
app.include_router(auth.router, prefix="/api")
app.include_router(plants.router, prefix="/api")
app.include_router(simulations.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(reagents.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(operator.router, prefix="/api")

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for container/orchestrator liveliness checks."""
    return {"status": "healthy", "service": "biomimetic-sim-api"}
