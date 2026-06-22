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
from app.game.utils import format_dt

from app.models.plant import Plant
from app.models.item import Item
from app.models.inventory import Inventory


router = APIRouter()

class WaterRequest(BaseModel):
    bed_id: int

class PlantRequest(BaseModel):
    plant_id: int

class HarvestRequest(BaseModel):
    bed_id: int

class UseItemRequest(BaseModel):
    bed_id: int


templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


def bed_to_dict(bed):
    return {
        "id": bed.id,
        "plant_name": bed.plant_name,
        "vitality": bed.vitality,
        "essence": bed.essence,
        "growth_stage": bed.growth_stage,
        "stage_name": bed.stage_name,
        "is_dead": bed.is_dead,
        "can_water": bed.can_water,
        "can_harvest": bed.can_harvest,
        "recovery_until": bed.recovery_until,  # ← сырой datetime для сравнения в шаблоне
        "recovery_until_str": format_dt(bed.recovery_until) if bed.recovery_until else None,  # ← для показа
        "hours_until_update": bed.hours_until_next_update,  # ← новое
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
     # Ежедневное обновление всех растений
    services.process_all_daily_updates(db, TEMP_PLAYER_ID)

    beds = services.get_player_garden(db, TEMP_PLAYER_ID)
    plants = db.query(Plant).all()
    beds_out = [bed_to_dict(bed) for bed in beds]

    # Считаем Искры Роста в инвентаре
    spark_item = db.query(Item).filter(Item.name == "Искра Роста").first()
    spark_count = 0
    if spark_item:
        spark_inv = db.query(Inventory).filter(
            Inventory.player_id == TEMP_PLAYER_ID,
            Inventory.item_id == spark_item.id
        ).first()
        if spark_inv:
            spark_count = spark_inv.quantity

    return templates.TemplateResponse("garden.html", {
        "request": request,
        "beds": beds_out,
        "plants": plants,
        "now": datetime.utcnow(),
        "spark_count": spark_count,
    })


@router.post("/garden/harvest")
def harvest_bed(request: HarvestRequest, db: Session = Depends(get_db)):
    try:
        result = services.harvest_bed(db, TEMP_PLAYER_ID, request.bed_id)
        return {"ok": True, **result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/garden/use-spark")
def use_growth_spark(request: UseItemRequest, db: Session = Depends(get_db)):
    try:
        bed = services.use_growth_spark(db, TEMP_PLAYER_ID, request.bed_id)
        return {
            "ok": True,
            "plant_name": bed.plant_name,
            "growth_stage": bed.growth_stage,
            "stage_name": bed.stage_name,
            "essence": bed.essence,
            "can_water": bed.can_water
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
