from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PlantRequest(BaseModel):
    plant_id: int

class GardenBedOut(BaseModel):
    id: int
    plant_name: Optional[str] = None
    planted_at: Optional[datetime] = None
    ready_at: Optional[datetime] = None
    moisture: int
    is_ready: bool = False

    class Config:
        from_attributes = True
        