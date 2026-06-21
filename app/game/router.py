from pathlib import Path
from datetime import datetime
from pydantic import BaseModel

from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.database import get_db
from app.core.config import TEMP_PLAYER_ID
from app.game import services
from app.models.plant import Plant
from app.models.player import Player


router = APIRouter()

class WaterRequest(BaseModel):
    bed_id: int

class PlantRequest(BaseModel):
    plant_id: int

templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


def format_dt(dt) -> str:
    if dt is None:
        return "—"
    return dt.strftime("%d.%m.%Y %H:%M")


def bed_to_dict(bed):
    """Превращает GardenBed в словарь для API и шаблонов."""
    return {
        "id": bed.id,
        "plant_name": bed.plant_name,
        "vitality": bed.vitality,
        "essence": bed.essence,
        "growth_stage": bed.growth_stage,
        "stage_name": bed.stage_name,
        "is_dead": bed.is_dead,
        "can_harvest": bed.can_harvest,
        "planted_at": format_dt(bed.planted_at),
    }


# === API ===

@router.get("/garden")
def get_garden(db: Session = Depends(get_db)):
    beds = services.get_player_garden(db, TEMP_PLAYER_ID)
    return [bed_to_dict(bed) for bed in beds]


@router.post("/garden/plant")
def plant_seed(request: PlantRequest, db: Session = Depends(get_db)):
    try:
        bed = services.plant_seed(db, TEMP_PLAYER_ID, request.plant_id)
        return bed_to_dict(bed)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/garden/water")
def water_bed(request: WaterRequest, db: Session = Depends(get_db)):
    try:
        bed = services.water_bed(db, TEMP_PLAYER_ID, request.bed_id)
        return {
            "ok": True,
            "plant_name": bed.plant_name,
            "vitality": bed.vitality,
            "essence": bed.essence,
            "growth_stage": bed.growth_stage,
            "stage_name": bed.stage_name
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# === СТРАНИЦА ===

@router.get("/garden/page", response_class=HTMLResponse)
def garden_page(request: Request, db: Session = Depends(get_db)):
    beds = services.get_player_garden(db, TEMP_PLAYER_ID)
    plants = db.query(Plant).all()
    beds_out = [bed_to_dict(bed) for bed in beds]
    return templates.TemplateResponse("garden.html", {
        "request": request,
        "beds": beds_out,
        "plants": plants
    })
