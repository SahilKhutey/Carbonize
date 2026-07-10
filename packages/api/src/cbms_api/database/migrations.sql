-- migrations.sql
-- Raw SQL schema migration file to initialize the biomimetic simulation database

-- Enable UUID extension if not enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Organizations Table
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    industry_type VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Plant Profiles Table
CREATE TABLE IF NOT EXISTS plant_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(100) NOT NULL,
    boiler_type VARCHAR(100) NOT NULL,
    exhaust_flow_rate NUMERIC(12, 2) NOT NULL,
    baseline_temperature NUMERIC(5, 2) NOT NULL,
    co2_concentration NUMERIC(4, 2) NOT NULL,
    so2_concentration NUMERIC(8, 2) NOT NULL,
    fly_ash_load NUMERIC(8, 2) NOT NULL,
    nox_concentration NUMERIC(8, 2) NOT NULL DEFAULT 500.0,
    extended_config JSONB DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_plant_profiles_org ON plant_profiles(organization_id);

-- Logistics Configurations Table
CREATE TABLE IF NOT EXISTS logistics_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plant_profile_id UUID NOT NULL UNIQUE REFERENCES plant_profiles(id) ON DELETE CASCADE,
    water_cost_per_kl NUMERIC(8, 2) NOT NULL,
    electricity_cost_per_kwh NUMERIC(6, 2) NOT NULL,
    chitosan_cost_per_kg NUMERIC(8, 2) NOT NULL,
    calcium_source_type VARCHAR(100) NOT NULL,
    calcium_cost_per_ton NUMERIC(8, 2) NOT NULL,
    local_brick_market_value NUMERIC(6, 2) NOT NULL,
    ccts_credit_price NUMERIC(8, 2) NOT NULL
);

-- Simulation Runs Table
CREATE TABLE IF NOT EXISTS simulation_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    plant_profile_id UUID NOT NULL REFERENCES plant_profiles(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    press_force_bar NUMERIC(5, 1) NOT NULL DEFAULT 200.0,
    enzyme_concentration_mg_l NUMERIC(4, 1) NOT NULL DEFAULT 12.0,
    chitosan_wt_pct NUMERIC(3, 1) NOT NULL DEFAULT 3.0,
    error_log TEXT,
    pdf_report_url VARCHAR(512),
    celery_task_id VARCHAR(255),
    input_hash VARCHAR(64),
    parameter_version VARCHAR(50) DEFAULT 'v2026.1',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_sim_runs_plant ON simulation_runs(plant_profile_id);
CREATE INDEX IF NOT EXISTS idx_sim_runs_org ON simulation_runs(organization_id);

-- Simulation Results Table
CREATE TABLE IF NOT EXISTS simulation_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    simulation_run_id UUID NOT NULL UNIQUE REFERENCES simulation_runs(id) ON DELETE CASCADE,
    co2_capture_efficiency_pct NUMERIC(5, 2) NOT NULL,
    so2_capture_efficiency_pct NUMERIC(5, 2) NOT NULL,
    predicted_block_strength_mpa NUMERIC(5, 2) NOT NULL,
    block_grade VARCHAR(100) NOT NULL,
    hourly_block_yield_kg NUMERIC(12, 2) NOT NULL,
    annual_block_count INTEGER NOT NULL,
    estimated_opex_per_ton_co2 NUMERIC(10, 2) NOT NULL,
    annual_ccts_revenue_inr NUMERIC(15, 2) NOT NULL,
    annual_block_revenue_inr NUMERIC(15, 2) NOT NULL,
    annual_opex_inr NUMERIC(15, 2) NOT NULL,
    annual_net_revenue_inr NUMERIC(15, 2) NOT NULL,
    capex_total_inr NUMERIC(15, 2) NOT NULL,
    simple_payback_months NUMERIC(6, 2) NOT NULL,
    npv_10yr_inr NUMERIC(15, 2) NOT NULL,
    irr_pct NUMERIC(6, 2) NOT NULL,
    mean_saturation_time_hours NUMERIC(8, 2) NOT NULL,
    p95_saturation_time_hours NUMERIC(8, 2) NOT NULL,
    cpcb_compliant BOOLEAN NOT NULL,
    uq_metrics JSONB DEFAULT '{}'::jsonb
);
