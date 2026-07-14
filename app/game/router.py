from pathlib import Path
from datetime import datetime
from pydantic import BaseModel

from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.database import get_db
from app.core import balance
from app.core.config import TEMP_PLAYER_ID

from app.game import services
from app.game import schemas
from app.game.utils import format_dt
from app.game.moon import get_moon_phase

from app.models.plant import Plant
from app.models.item import Item
from app.models.inventory import Inventory
from app.models.player import Player
from app.models.garden_bed import GardenBed
from app.models.care_log import CareLog


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
    plant = bed.plant
    icon = None
    if plant:
        icon = plant.get_icon_for_stage(bed.growth_stage) or plant.icon_seed
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
        "can_clean": bed.can_clean,
        "essence_bar_max": balance.ESSENCE_BAR_MAX,
        "can_moon_bath": bed.can_moon_bath,
        "icon": bed.plant.icon if bed.plant and bed.plant.icon else None,
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
        spark_invs = db.query(Inventory).filter(
            Inventory.player_id == TEMP_PLAYER_ID,
            Inventory.item_id == spark_item.id
        ).all()
        spark_count = sum(inv.quantity for inv in spark_invs)
    player = db.query(Player).filter(Player.id == TEMP_PLAYER_ID).first()    

    return templates.TemplateResponse("garden.html", {
        "request": request,
        "beds": beds_out,
        "plants": plants,
        "now": datetime.utcnow(),
        "spark_count": spark_count,
        "coins": player.coins if player else 0,
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

@router.post("/garden/clean", response_model=schemas.CleanResultOut)
def clean_bed(request: schemas.CleanRequest, db: Session = Depends(get_db)):
    try:
        bed = services.clean_bed(db, TEMP_PLAYER_ID, request.bed_id)
        return {
            "ok": True,
            "plant_name": bed.plant_name,
            "vitality": bed.vitality,
            "essence": bed.essence
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/garden/moon-bath", response_model=schemas.MoonBathResultOut)
def moon_bath(request: schemas.MoonBathRequest, db: Session = Depends(get_db)):
    try:
        bed = services.moon_bath(db, TEMP_PLAYER_ID, request.bed_id)
        moon = get_moon_phase()
        return {
            "ok": True,
            "plant_name": bed.plant_name,
            "vitality": bed.vitality,
            "essence": bed.essence,
            "moon_phase": moon["name"],
            "moon_emoji": moon["emoji"],
            "bonus": moon["essence_bonus"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/moon")
def moon_info():
    moon = get_moon_phase()
    return moon
    
@router.get("/garden/plant/{bed_id}", response_class=HTMLResponse)
def plant_page(request: Request, bed_id: int, db: Session = Depends(get_db)):
    bed = db.query(GardenBed).filter(
        GardenBed.id == bed_id,
        GardenBed.player_id == TEMP_PLAYER_ID
    ).first()
    if not bed:
        raise HTTPException(status_code=404, detail="Грядка не найдена")

    logs = db.query(CareLog).filter(
        CareLog.garden_bed_id == bed_id,
        CareLog.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
    ).order_by(CareLog.created_at.asc()).all()

    logs_data = []
    for log in logs:
        logs_data.append({
            "time": log.created_at.strftime("%H:%M"),
            "action_name": log.action_name,
            "effect": log.effect,
            "mood": log.mood,
            "details": log.details,
        })

    spark_item = db.query(Item).filter(Item.name == "Искра Роста").first()
    spark_count = 0
    if spark_item:
        spark_inv = db.query(Inventory).filter(
            Inventory.player_id == TEMP_PLAYER_ID,
            Inventory.item_id == spark_item.id
        ).first()
        if spark_inv:
            spark_count = spark_inv.quantity

    return templates.TemplateResponse("plant_detail.html", {
        "request": request,
        "bed": bed_to_dict(bed),
        "plant_name": bed.plant_name,
        "logs": logs_data,
        "spark_count": spark_count,
        "now": datetime.utcnow()
    })
    