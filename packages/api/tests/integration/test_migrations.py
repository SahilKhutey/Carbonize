"""Integration tests for Alembic database migrations."""

import os
import subprocess
import pytest
from pathlib import Path


def test_alembic_offline_sql_generation():
    """Verify that Alembic generates clean, valid PostgreSQL DDL up to head revision."""
    api_dir = Path(__file__).parent.parent.parent
    env = dict(os.environ)
    env["PYTHONPATH"] = str(api_dir / "src")

    res = subprocess.run(
        ["alembic", "upgrade", "head", "--sql"],
        cwd=str(api_dir),
        env=env,
        capture_output=True,
        text=True,
        check=True
    )

    stdout = res.stdout
    assert "CREATE TABLE organizations" in stdout
    assert "CREATE TABLE simulation_runs" in stdout
    assert "CREATE TABLE sensor_readings" in stdout
    assert "b1c2d3e4f5a6" in stdout
