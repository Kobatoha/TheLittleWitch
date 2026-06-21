from pathlib import Path
from datetime import datetime
from pydantic import BaseModel

from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.database import get_db
from app.core.config import TEMP_PLAYER_ID
from app.game import services, schemas
from app.models.plant import Plant
from app.models.player import Player


router = APIRouter()

class WaterRequest(BaseModel):
    bed_id: int

def format_dt(dt) -> str:
    """Красиво форматирует datetime для сада."""
    if dt is None:
        return "—"
    return dt.strftime("%d.%m.%Y %H:%M")

def _is_ready(bed) -> bool:
    return bool(bed.ready_at and bed.ready_at <= datetime.utcnow())


def bed_to_api(bed) -> schemas.GardenBedOut:
    return schemas.GardenBedOut(
        id=bed.id,
        plant_name=bed.plant.name if bed.plant else None,
        planted_at=bed.planted_at,
        ready_at=bed.ready_at,
        moisture=bed.moisture,
        is_ready=_is_ready(bed),
    )


def bed_to_template(bed):
    is_ready = _is_ready(bed)

    if bed.ready_at and not is_ready:
        delta = bed.ready_at - datetime.utcnow()
        minutes_left = int(delta.total_seconds() / 60)
        if minutes_left < 1:
            time_left = "Меньше минуты"
        elif minutes_left == 1:
            time_left = "1 минута"
        elif minutes_left < 5:
            time_left = f"{minutes_left} минуты"
        else:
            time_left = f"{minutes_left} минут"
    elif is_ready:
        time_left = "✅ Готово!"
    else:
        time_left = "—"

    return {
        "id": bed.id,
        "plant_name": bed.plant_name,
        "planted_at": format_dt(bed.planted_at),
        "ready_at": format_dt(bed.ready_at),
        "time_left": time_left,
        "moisture": bed.moisture,
        "vitality": bed.vitality,
        "essence": bed.essence,
        "growth_stage": bed.growth_stage,
        "stage_name": bed.stage_name,
        "is_dead": bed.is_dead,
        "can_harvest": bed.can_harvest,
        "is_ready": is_ready,
    }


@router.get("/garden", response_model=list[schemas.GardenBedOut])
def get_garden(db: Session = Depends(get_db)):
    beds = services.get_player_garden(db, TEMP_PLAYER_ID)
    return [bed_to_api(bed) for bed in beds]


@router.post("/garden/plant", response_model=schemas.GardenBedOut)
def plant_seed(request: schemas.PlantRequest, db: Session = Depends(get_db)):
    try:
        bed = services.plant_seed(db, TEMP_PLAYER_ID, request.plant_id)
        return bed_to_api(bed)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

@router.get("/garden/page", response_class=HTMLResponse)
def garden_page(request: Request, db: Session = Depends(get_db)):
    beds = services.get_player_garden(db, TEMP_PLAYER_ID)
    plants = db.query(Plant).all()

    beds_out = [bed_to_template(bed) for bed in beds]

    return templates.TemplateResponse("garden.html", {
        "request": request,
        "beds": beds_out,
        "plants": plants
    })

@router.post("/garden/water")
def water_bed(request: WaterRequest, db: Session = Depends(get_db)):
    try:
        bed = services.water_bed_new(db, TEMP_PLAYER_ID, request.bed_id)
        player = db.query(Player).filter(Player.id == TEMP_PLAYER_ID).first()
        return {
            "ok": True,
            "plant_name": bed.plant.name if bed.plant else "?",
            "vitality": bed.vitality,
            "essence": bed.essence,
            "growth_stage": bed.growth_stage,
            "stage_name": bed.stage_name,
            "energy_left": player.energy
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
