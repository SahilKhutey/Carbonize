# ============================================================================
# Base Python image for all Python services
# Used by: api, worker, sim-core
# ============================================================================
# Multi-stage: build tools → runtime (smaller final image)

# ============================================================================
# Stage 1: Builder (with build tools)
# ============================================================================
FROM python:3.12-slim-bookworm AS builder

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    gfortran \
    libpq-dev \
    libhdf5-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_VERSION=1.8.3
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_NO_INTERACTION=1
RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

WORKDIR /app

# Copy dependency files first (for Docker layer caching)
COPY pyproject.toml poetry.lock ./

# Install dependencies (no dev deps in production)
RUN poetry install --without dev --no-root

# ============================================================================
# Stage 2: Runtime (minimal, no build tools)
# ============================================================================
FROM python:3.12-slim-bookworm AS runtime

# Runtime system dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libgomp1 \
    libhdf5-103 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --system --gid 1000 app && \
    useradd --system --uid 1000 --gid 1000 --home /app --shell /bin/bash app

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --from=builder --chown=app:app /app/pyproject.toml /app/poetry.lock ./

# Activate venv in PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONFAULTHANDLER=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Drop to non-root
USER app
