from sqlalchemy.orm import Session

from fastapi import Depends

from app.core.database import get_db
from app.core.config import TEMP_PLAYER_ID
from app.game.services.garden import GardenService


def get_garden_service(db: Session = Depends(get_db)) -> GardenService:
    return GardenService(db, TEMP_PLAYER_ID)
    