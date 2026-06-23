from typing import List, Optional

from pydantic import BaseModel

# === ЗАПРОСЫ ===

class PlantRequest(BaseModel):
    plant_id: int

class WaterRequest(BaseModel):
    bed_id: int

class HarvestRequest(BaseModel):
    bed_id: int

class UseItemRequest(BaseModel):
    bed_id: int

# === ОТВЕТЫ ===

class GardenBedOut(BaseModel):
    id: int
    plant_name: Optional[str] = None
    vitality: int
    essence: int
    growth_stage: int
    stage_name: str
    is_dead: bool
    can_water: bool
    can_harvest: bool
    recovery_until: Optional[str] = None
    recovery_until_str: Optional[str] = None
    hours_until_update: int
    planted_at: Optional[str] = None


class HarvestItemOut(BaseModel):
    name: str
    quantity: int
    quality: str


class BonusItemOut(BaseModel):
    name: str
    rarity: str


class HarvestResultOut(BaseModel):
    ok: bool = True
    plant_name: str
    stage: str
    main_harvest: List[HarvestItemOut]
    bonus_harvest: List[BonusItemOut]
    rare_harvest: List[BonusItemOut]


class WaterResultOut(BaseModel):
    ok: bool = True
    plant_name: str
    vitality: int
    essence: int
    growth_stage: int
    stage_name: str


class SparkResultOut(BaseModel):
    ok: bool = True
    plant_name: str
    growth_stage: int
    stage_name: str
    essence: int
    can_water: bool


class InventoryItemOut(BaseModel):
    id: int
    item_name: str
    item_type: str
    rarity: str
    quality: str
    quantity: int
    description: str
    created_at: Optional[str] = None
    
class CleanRequest(BaseModel):
    bed_id: int

class CleanResultOut(BaseModel):
    ok: bool = True
    plant_name: str
    vitality: int
    essence: int