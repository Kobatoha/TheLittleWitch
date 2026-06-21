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

@router.get("/garden", response_model=list[schemas.GardenBedOut])
def get_garden(db: Session = Depends(get_db)):
    beds = services.get_player_garden(db, TEMP_PLAYER_ID)
    result = []
    for bed in beds:
        result.append(bed_to_dict(bed))
    return result

@router.post("/garden/plant", response_model=schemas.GardenBedOut)
def plant_seed(request: schemas.PlantRequest, db: Session = Depends(get_db)):
    try:
        bed = services.plant_seed(db, TEMP_PLAYER_ID, request.plant_id)
        return bed_to_dict(bed)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

@router.get("/garden/page", response_class=HTMLResponse)
def garden_page(request: Request, db: Session = Depends(get_db)):
    beds = services.get_player_garden(db, TEMP_PLAYER_ID)
    plants = db.query(Plant).all()

    beds_out = []
    for bed in beds:
        beds_out.append(bed_to_dict(bed))

    return templates.TemplateResponse("garden.html", {
        "request": request,
        "beds": beds_out,
        "plants": plants
    })

def bed_to_dict(bed):
    return {
        "id": bed.id,
        "plant_name": bed.plant.name if bed.plant else None,
        "planted_at": bed.planted_at,
        "ready_at": bed.ready_at,
        "moisture": bed.moisture,
        "is_ready": bed.ready_at and bed.ready_at <= datetime.utcnow()
    }

@router.post("/garden/water")
def water_bed(request: WaterRequest, db: Session = Depends(get_db)):
    try:
        bed = services.water_bed(db, TEMP_PLAYER_ID, request.bed_id)
        return {
            "ok": True,
            "plant_name": bed.plant.name if bed.plant else "?",
            "moisture": bed.moisture,
            "ready_at": bed.ready_at,
            "energy_left": db.query(Player).filter(Player.id == TEMP_PLAYER_ID).first().energy
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
