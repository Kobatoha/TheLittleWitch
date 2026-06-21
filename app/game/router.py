from pathlib import Path

from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.database import get_db
from app.game import services, schemas
from app.models.plant import Plant


router = APIRouter()

# Временно захардкодим player_id = 1, потом заменим на авторизацию
TEMP_PLAYER_ID = 1

@router.get("/garden", response_model=list[schemas.GardenBedOut])
def get_garden(db: Session = Depends(get_db)):
    beds = services.get_player_garden(db, TEMP_PLAYER_ID)
    result = []
    for bed in beds:
        result.append(schemas.GardenBedOut(
            id=bed.id,
            plant_name=bed.plant.name if bed.plant else None,
            planted_at=bed.planted_at,
            ready_at=bed.ready_at,
            moisture=bed.moisture,
            is_ready=bed.ready_at and bed.ready_at <= __import__("datetime").datetime.utcnow()
        ))
    return result

@router.post("/garden/plant", response_model=schemas.GardenBedOut)
def plant_seed(request: schemas.PlantRequest, db: Session = Depends(get_db)):
    try:
        bed = services.plant_seed(db, TEMP_PLAYER_ID, request.plant_id)
        return schemas.GardenBedOut(
            id=bed.id,
            plant_name=bed.plant.name if bed.plant else None,
            planted_at=bed.planted_at,
            ready_at=bed.ready_at,
            moisture=bed.moisture,
            is_ready=False
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

@router.get("/garden/page", response_class=HTMLResponse)
def garden_page(request: Request, db: Session = Depends(get_db)):
    beds = services.get_player_garden(db, TEMP_PLAYER_ID)
    plants = db.query(Plant).all()

    beds_out = []
    for bed in beds:
        beds_out.append({
            "id": bed.id,
            "plant_name": bed.plant.name if bed.plant else None,
            "planted_at": bed.planted_at,
            "ready_at": bed.ready_at,
            "moisture": bed.moisture,
            "is_ready": bed.ready_at and bed.ready_at <= __import__("datetime").datetime.utcnow()
        })

    return templates.TemplateResponse("garden.html", {
        "request": request,
        "beds": beds_out,
        "plants": plants
    })