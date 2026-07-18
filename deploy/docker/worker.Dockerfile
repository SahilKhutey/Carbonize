# ============================================================================
# worker: Celery worker for async tasks
# 
# Multi-stage build (shares base image with API)
# ============================================================================

ARG BASE_IMAGE=python-base

# ============================================================================
# Stage 1: Dependencies
# ============================================================================
FROM ${BASE_IMAGE} AS deps

USER root

WORKDIR /app

# Worker system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./
COPY packages/shared/ /app/packages/shared/
COPY packages/workers/ /app/packages/workers/
COPY packages/sim-core/ /app/packages/sim-core/
# Copy packages/api (needed for schemas)
COPY packages/api/ /app/packages/api/

RUN poetry install --no-root

# ============================================================================
# Stage 2: Test
# ============================================================================
FROM deps AS test

RUN poetry run pytest packages/workers/tests/ -v --tb=short

# ============================================================================
# Stage 3: Runtime
# ============================================================================
FROM ${BASE_IMAGE} AS runtime

WORKDIR /app

COPY --from=deps --chown=app:app /app/.venv /app/.venv
COPY --from=deps --chown=app:app /app/packages /app/packages
COPY --from=deps --chown=app:app /app/pyproject.toml /app/poetry.lock ./

USER app

# Healthcheck (Celery ping)
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD celery -A cbms_workers.celery_app inspect ping || exit 1

CMD ["celery", "-A", "cbms_workers.celery_app", "worker", "--loglevel=info", "-Q", "critical,compute_heavy,reporting,quick_sim,low_priority", "--concurrency=4"]
