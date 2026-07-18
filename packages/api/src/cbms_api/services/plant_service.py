"""
services/plant_service.py
Service layer implementing CRUD operations for PlantProfile database models.
"""

from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from cbms_api.database.models import PlantProfile, LogisticsConfig
from cbms_shared.exceptions import NotFoundError, ValidationFailedError

class PlantService:
    """Enforces multi-tenant business rules and database persistence for plants."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def create_plant(self, org_id: UUID, schema) -> PlantProfile:
        """Create a new industrial emissions profile and associated logistics context."""
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
        self.db.add(plant)
        await self.db.flush()
        
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
        self.db.add(logistics)
        await self.db.commit()
        
        result = await self.db.execute(
            select(PlantProfile)
            .options(selectinload(PlantProfile.logistics))
            .filter(PlantProfile.id == plant.id)
        )
        return result.scalars().first()
        
    async def get_plant(self, plant_id: UUID, org_id: UUID) -> PlantProfile:
        """Fetch plant profile under RLS organization scope."""
        result = await self.db.execute(
            select(PlantProfile)
            .options(selectinload(PlantProfile.logistics))
            .filter(PlantProfile.id == plant_id)
            .filter(PlantProfile.organization_id == org_id)
        )
        plant = result.scalars().first()
        if not plant:
            raise NotFoundError("Plant profile not found.")
        return plant
        
    async def delete_plant(self, plant_id: UUID, org_id: UUID) -> None:
        """Soft-delete plant profile if no pending jobs match."""
        plant = await self.get_plant(plant_id, org_id)
        await self.db.delete(plant)
        await self.db.commit()
