# ============================================================================
# sim-core: scientific simulation library
# 
# This is a LIBRARY, not a service. It has no HTTP server.
# It's a dependency of api and worker.
#
# Multi-stage build for minimum final image size.
# ============================================================================

ARG BASE_IMAGE=python-base

# ============================================================================
# Stage 1: Builder
# ============================================================================
FROM ${BASE_IMAGE} AS builder

WORKDIR /app

# Copy only sim-core package first
COPY packages/sim-core/ /app/packages/sim-core/
COPY packages/shared/ /app/packages/shared/
COPY pyproject.toml poetry.lock ./

# Install sim-core and its dependencies
RUN poetry install --no-root

# Copy sim-core source for packaging
COPY packages/ /app/packages/

# Install sim-core as a package
RUN poetry install --no-root

# ============================================================================
# Stage 2: Test runner (for CI)
# ============================================================================
FROM builder AS tester

# Run tests
RUN poetry run pytest packages/sim-core/tests/ -v --tb=short

# ============================================================================
# Stage 3: Runtime (minimal, just the library installed)
# ============================================================================
FROM ${BASE_IMAGE} AS runtime

WORKDIR /app

# Copy installed packages
COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --from=builder --chown=app:app /app/packages /app/packages
COPY --from=builder --chown=app:app /app/pyproject.toml /app/poetry.lock ./

# Verify sim-core is importable
RUN python -c "import cbms_sim; print('sim-core OK')"

# Runtime doesn't need CMD (library only)
# CMD can be overridden by parent image
CMD ["python", "-c", "import cbms_sim; print('sim-core loaded')"]
