"""Integration tests for Alembic database migrations."""

import os
import subprocess
import pytest
from pathlib import Path


def test_alembic_offline_sql_generation():
    """Verify that Alembic generates clean, valid PostgreSQL DDL up to head revision."""
    api_dir = Path(__file__).parent.parent.parent
    sim_core_src = str(api_dir.parent / "sim-core" / "src")
    shared_src = str(api_dir.parent / "shared" / "src")
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{api_dir / 'src'}{os.pathsep}{sim_core_src}{os.pathsep}{shared_src}"

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
