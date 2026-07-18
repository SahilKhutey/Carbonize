# ============================================================================
# api: FastAPI application server
# 
# Multi-stage build:
# 1. Builder: install deps, compile
# 2. Test: run unit/integration tests
# 3. Runtime: minimal image with just app + deps
# ============================================================================

ARG BASE_IMAGE=python-base

# ============================================================================
# Stage 1: Dependencies
# ============================================================================
FROM ${BASE_IMAGE} AS deps

WORKDIR /app

# Install API-specific system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml poetry.lock ./
COPY packages/shared/ /app/packages/shared/
COPY packages/api/ /app/packages/api/
COPY packages/sim-core/ /app/packages/sim-core/
# Copy packages/workers (needed for tasks)
COPY packages/workers/ /app/packages/workers/

# Install API and all its deps
RUN poetry install --no-root

# ============================================================================
# Stage 2: Test
# ============================================================================
FROM deps AS test

# Run tests
RUN poetry run pytest packages/api/tests/ -v --tb=short

# ============================================================================
# Stage 3: Runtime
# ============================================================================
FROM ${BASE_IMAGE} AS runtime

WORKDIR /app

# Copy installed virtualenv
COPY --from=deps --chown=app:app /app/.venv /app/.venv
COPY --from=deps --chown=app:app /app/packages /app/packages
COPY --from=deps --chown=app:app /app/pyproject.toml /app/poetry.lock ./

# Healthcheck (uses the /health endpoint)
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run as non-root
USER app

# Default command (overridden in docker-compose)
CMD ["uvicorn", "cbms_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
