"""
api/routes/plants.py
Endpoints for managing industrial plant profiles.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_active_tenant_id
from database.models import PlantProfile, LogisticsConfig
from cbms_api.schemas.plant import PlantProfileCreateRequest
from cbms_api.middleware.rate_limiting import rate_limit_write, rate_limit_read

router = APIRouter(prefix="/plants", tags=["Plants"])

@router.post("", response_model=None, status_code=status.HTTP_201_CREATED)
@rate_limit_write(limit="30/minute")
async def create_plant(
    request: Request,
    schema: PlantProfileCreateRequest,
    db: AsyncSession = Depends(get_db),
    org_id: UUID = Depends(get_active_tenant_id)
):
    """
    Creates a new industrial plant profile and its associated logistics config.
    """
    # Create the PlantProfile
    plant = PlantProfile(
        organization_id=org_id,
        name=schema.name,
        location=schema.location,
        boiler_type=schema.boiler_type.value,
        exhaust_flow_rate=schema.exhaust_flow_rate,
        baseline_temperature=schema.baseline_temperature,
        co2_concentration=schema.co2_concentration,
        so2_concentration=schema.so2_concentration,
        fly_ash_load=schema.fly_ash_load,
        nox_concentration=schema.nox_concentration
    )
    db.add(plant)
    await db.flush()  # Obtain plant.id for foreign key

    # Create the LogisticsConfig
    logistics = LogisticsConfig(
        plant_profile_id=plant.id,
        water_cost_per_kl=schema.water_cost_per_kl,
        electricity_cost_per_kwh=schema.electricity_cost_per_kwh,
        chitosan_cost_per_kg=schema.chitosan_cost_per_kg,
        calcium_source_type=schema.calcium_source_type.value,
        calcium_cost_per_ton=schema.calcium_cost_per_ton,
        local_brick_market_value=schema.local_brick_market_value,
        ccts_credit_price=schema.ccts_credit_price
    )
    db.add(logistics)
    await db.commit()
    
    # Return complete object with loaded relationships
    result = await db.execute(
        select(PlantProfile)
        .options(selectinload(PlantProfile.logistics))
        .filter(PlantProfile.id == plant.id)
    )
    return result.scalars().first()

@router.get("", response_model=None)
@rate_limit_read(limit="300/minute")
async def list_plants(
    request: Request,
    db: AsyncSession = Depends(get_db),
    org_id: UUID = Depends(get_active_tenant_id)
):
    """
    Lists all available plant profiles for the current tenant.
    """
    result = await db.execute(
        select(PlantProfile)
        .options(selectinload(PlantProfile.logistics))
        .filter(PlantProfile.organization_id == org_id)
    )
    return result.scalars().all()

@router.get("/{plant_id}", response_model=None)
@rate_limit_read(limit="600/minute")
async def get_plant(
    request: Request,
    plant_id: UUID,
    db: AsyncSession = Depends(get_db),
    org_id: UUID = Depends(get_active_tenant_id)
):
    """
    Fetches a specific plant profile by ID under tenant scope.
    """
    result = await db.execute(
        select(PlantProfile)
        .options(selectinload(PlantProfile.logistics))
        .filter(PlantProfile.id == plant_id)
        .filter(PlantProfile.organization_id == org_id)
    )
    plant = result.scalars().first()
    if not plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plant profile not found."
        )
    return plant
