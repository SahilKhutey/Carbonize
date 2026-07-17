"""
database/models.py
SQLAlchemy 2.0 async ORM models for the simulation platform.
"""

from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List
from sqlalchemy import (
    String, Numeric, Integer, ForeignKey, DateTime, Boolean, Text, Index
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry_type: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    plants: Mapped[List["PlantProfile"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    simulations: Mapped[List["SimulationRun"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )


class PlantProfile(Base):
    __tablename__ = "plant_profiles"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    boiler_type: Mapped[str] = mapped_column(String(100), nullable=False)

    exhaust_flow_rate: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    baseline_temperature: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    co2_concentration: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    so2_concentration: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    fly_ash_load: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    nox_concentration: Mapped[float] = mapped_column(Numeric(8, 2), default=500.0)

    # JSONB for flexible extended parameters
    extended_config: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    organization: Mapped["Organization"] = relationship(back_populates="plants")
    logistics: Mapped[Optional["LogisticsConfig"]] = relationship(
        back_populates="plant", cascade="all, delete-orphan", uselist=False
    )
    simulations: Mapped[List["SimulationRun"]] = relationship(
        back_populates="plant", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("idx_plant_profiles_org", "organization_id"),)


class LogisticsConfig(Base):
    __tablename__ = "logistics_configs"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    plant_profile_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("plant_profiles.id", ondelete="CASCADE"),
        unique=True
    )
    water_cost_per_kl: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    electricity_cost_per_kwh: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    chitosan_cost_per_kg: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    calcium_source_type: Mapped[str] = mapped_column(String(100), nullable=False)
    calcium_cost_per_ton: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    local_brick_market_value: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    ccts_credit_price: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)

    plant: Mapped["PlantProfile"] = relationship(back_populates="logistics")


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    plant_profile_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("plant_profiles.id", ondelete="CASCADE")
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    press_force_bar: Mapped[float] = mapped_column(Numeric(5, 1), default=200.0)
    enzyme_concentration_mg_l: Mapped[float] = mapped_column(Numeric(4, 1), default=12.0)
    chitosan_wt_pct: Mapped[float] = mapped_column(Numeric(3, 1), default=3.0)
    error_log: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pdf_report_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    celery_task_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    input_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    parameter_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, default="v2026.1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    organization: Mapped["Organization"] = relationship(back_populates="simulations")
    plant: Mapped["PlantProfile"] = relationship(back_populates="simulations")
    result: Mapped[Optional["SimulationResult"]] = relationship(
        back_populates="run", cascade="all, delete-orphan", uselist=False
    )

    __table_args__ = (
        Index("idx_sim_runs_plant", "plant_profile_id"),
        Index("idx_sim_runs_org", "organization_id"),
    )


class SimulationResult(Base):
    __tablename__ = "simulation_results"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    simulation_run_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("simulation_runs.id", ondelete="CASCADE"),
        unique=True
    )

    co2_capture_efficiency_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    so2_capture_efficiency_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    predicted_block_strength_mpa: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    block_grade: Mapped[str] = mapped_column(String(100), nullable=False)
    hourly_block_yield_kg: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    annual_block_count: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_opex_per_ton_co2: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Financial indicators
    annual_ccts_revenue_inr: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    annual_block_revenue_inr: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    annual_opex_inr: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    annual_net_revenue_inr: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    capex_total_inr: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    simple_payback_months: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    npv_10yr_inr: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    irr_pct: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    
    # Stochastic process results
    mean_saturation_time_hours: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    p95_saturation_time_hours: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    cpcb_compliant: Mapped[bool] = mapped_column(Boolean, nullable=False)
    uq_metrics: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)

    run: Mapped["SimulationRun"] = relationship(back_populates="result")
