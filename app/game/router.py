from pathlib import Path
from datetime import datetime
from pydantic import BaseModel

from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.constants import ITEM_GROWTH_SPARK
from app.core.database import get_db
from app.core import balance
from app.core.config import TEMP_PLAYER_ID
from app.core.exceptions import GameError, ErrorCode

from app.game import services
from app.game import schemas
from app.game.services import GardenService
from app.game.utils import format_dt
from app.game.moon import get_moon_phase
from app.core.dependencies import get_garden_service

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


def bed_to_dict(bed: GardenBed) -> dict:
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
        "recovery_until": bed.recovery_until,
        "recovery_until_str": format_dt(bed.recovery_until) if bed.recovery_until else None,
        "hours_until_update": bed.hours_until_next_update,
        "planted_at": format_dt(bed.planted_at),
        "can_clean": bed.can_clean,
        "essence_bar_max": balance.ESSENCE_BAR_MAX,
        "can_moon_bath": bed.can_moon_bath,
        "icon": bed.plant.get_icon_for_stage(bed.growth_stage) if bed.plant else None,
    }


@router.get("/garden")
def get_garden(garden: GardenService = Depends(get_garden_service)) -> list[dict[str, str]]:
    beds = garden.get_player_garden()
    return [bed_to_dict(bed) for bed in beds]


@router.post("/garden/plant")
def plant_seed(request: PlantRequest, garden: GardenService = Depends(get_garden_service)):
    bed = garden.plant_seed(request.plant_id)
    return bed_to_dict(bed)


@router.post("/garden/water")
def water_bed(request: WaterRequest, garden: GardenService = Depends(get_garden_service)) -> dict:
    bed = garden.water_bed(request.bed_id)
    return {
        "ok": True,
        "plant_name": bed.plant_name,
        "vitality": bed.vitality,
        "essence": bed.essence,
        "growth_stage": bed.growth_stage,
        "stage_name": bed.stage_name
    }


@router.get("/garden/page", response_class=HTMLResponse)
def garden_page(request: Request, db: Session = Depends(get_db), garden: GardenService = Depends(get_garden_service)):
    garden.process_all_daily_updates()

    beds = garden.get_player_garden()
    plants = db.query(Plant).all()
    beds_out = [bed_to_dict(bed) for bed in beds]

    spark_item = db.query(Item).filter(Item.name == ITEM_GROWTH_SPARK).first()
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
def harvest_bed(request: HarvestRequest, garden: GardenService = Depends(get_garden_service)):
    result = garden.harvest_bed(request.bed_id)
    return {"ok": True, **result}


@router.post("/garden/use-spark")
def use_growth_spark(request: UseItemRequest, garden: GardenService = Depends(get_garden_service)):
    bed = garden.use_growth_spark(request.bed_id)
    return {
        "ok": True,
        "plant_name": bed.plant_name,
        "growth_stage": bed.growth_stage,
        "stage_name": bed.stage_name,
        "essence": bed.essence,
        "can_water": bed.can_water
    }


@router.post("/garden/clean", response_model=schemas.CleanResultOut)
def clean_bed(request: schemas.CleanRequest, garden: GardenService = Depends(get_garden_service)):
    bed = garden.clean_bed(request.bed_id)
    return {
        "ok": True,
        "plant_name": bed.plant_name,
        "vitality": bed.vitality,
        "essence": bed.essence
    }


@router.post("/garden/moon-bath", response_model=schemas.MoonBathResultOut)
def moon_bath(request: schemas.MoonBathRequest, garden: GardenService = Depends(get_garden_service)):
    bed = garden.moon_bath(request.bed_id)
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
        raise GameError(ErrorCode.BED_NOT_FOUND)

    logs = db.query(CareLog).filter(
        bed_id == CareLog.garden_bed_id,
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

    spark_item = db.query(Item).filter(Item.name == ITEM_GROWTH_SPARK).first()
    spark_count = 0
    if spark_item:
        spark_inv = db.query(Inventory).filter(
            Inventory.player_id == TEMP_PLAYER_ID,
            spark_item.id == Inventory.item_id
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


@router.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request, db: Session = Depends(get_db)):
    profile = services.get_player_profile(db, TEMP_PLAYER_ID)

    spark_count = 0
    spark_item = db.query(Item).filter(Item.name == ITEM_GROWTH_SPARK).first()
    if spark_item:
        spark_inv = db.query(Inventory).filter(
            Inventory.player_id == TEMP_PLAYER_ID,
            Inventory.item_id == spark_item.id
        ).first()
        if spark_inv:
            spark_count = spark_inv.quantity

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "profile": profile,
        "spark_count": spark_count,
        "coins": profile["coins"],
    })
