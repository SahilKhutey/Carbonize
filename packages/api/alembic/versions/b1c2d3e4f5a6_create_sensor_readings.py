"""create_sensor_readings

Revision ID: b1c2d3e4f5a6
Revises: 914b3d47d408
Create Date: 2026-07-20 08:42:00.000000

Creates the sensor_readings hypertable for time-series storage of both
real physical-sensor data and simulation-derived readings.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB

# revision identifiers
revision: str = "b1c2d3e4f5a6"
down_revision: Union[str, Sequence[str], None] = "914b3d47d408"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create sensor_readings table with composite indexes."""
    op.create_table(
        "sensor_readings",
        sa.Column("id",               PGUUID(as_uuid=True), primary_key=True),
        sa.Column("reading_id",        PGUUID(as_uuid=True), nullable=False),
        sa.Column("timestamp",         sa.DateTime(timezone=True), nullable=False),
        sa.Column("measurement_type",  sa.String(50),  nullable=False),
        sa.Column("value",             sa.Float,       nullable=False),
        sa.Column("unit",              sa.String(20),  nullable=False),
        sa.Column("quality",           sa.String(20),  server_default="good"),
        sa.Column("sensor_id",         sa.String(100), nullable=True),
        sa.Column("uncertainty",       sa.Float,       nullable=True),
        sa.Column("source",            sa.String(50),  nullable=False),
        sa.Column("source_version",    sa.String(50),  nullable=False),
        sa.Column("plant_id",          PGUUID(as_uuid=True), nullable=False),
        sa.Column("simulation_id",     PGUUID(as_uuid=True), nullable=True),
        sa.Column("extra_metadata",    JSONB, server_default="{}"),
    )

    # Single-column indexes
    op.create_index("ix_readings_reading_id",  "sensor_readings", ["reading_id"])
    op.create_index("ix_readings_timestamp",   "sensor_readings", ["timestamp"])
    op.create_index("ix_readings_mtype",       "sensor_readings", ["measurement_type"])
    op.create_index("ix_readings_sensor_id",   "sensor_readings", ["sensor_id"])
    op.create_index("ix_readings_source",      "sensor_readings", ["source"])
    op.create_index("ix_readings_plant_id",    "sensor_readings", ["plant_id"])
    op.create_index("ix_readings_sim_id",      "sensor_readings", ["simulation_id"])

    # Composite indexes for time-series queries
    op.create_index("ix_readings_plant_time",       "sensor_readings", ["plant_id", "timestamp"])
    op.create_index("ix_readings_type_time",        "sensor_readings", ["measurement_type", "timestamp"])
    op.create_index("ix_readings_plant_type_time",  "sensor_readings", ["plant_id", "measurement_type", "timestamp"])


def downgrade() -> None:
    """Drop sensor_readings table and all its indexes."""
    op.drop_index("ix_readings_plant_type_time", table_name="sensor_readings")
    op.drop_index("ix_readings_type_time",       table_name="sensor_readings")
    op.drop_index("ix_readings_plant_time",      table_name="sensor_readings")
    op.drop_index("ix_readings_sim_id",          table_name="sensor_readings")
    op.drop_index("ix_readings_plant_id",        table_name="sensor_readings")
    op.drop_index("ix_readings_source",          table_name="sensor_readings")
    op.drop_index("ix_readings_sensor_id",       table_name="sensor_readings")
    op.drop_index("ix_readings_mtype",           table_name="sensor_readings")
    op.drop_index("ix_readings_timestamp",       table_name="sensor_readings")
    op.drop_index("ix_readings_reading_id",      table_name="sensor_readings")
    op.drop_table("sensor_readings")
