from pathlib import Path

from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.config import TEMP_PLAYER_ID
from app.core.balance import QUALITY_NORMAL
from app.core.database import get_db
from app.game.utils import format_dt
from app.models.inventory import Inventory
from app.models.player import Player


router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


@router.get("/inventory", response_class=HTMLResponse)
def inventory_page(request: Request, db: Session = Depends(get_db)):
    inventory_items = db.query(Inventory).filter(
        Inventory.player_id == TEMP_PLAYER_ID,
        Inventory.quantity > 0
    ).order_by(Inventory.created_at.desc()).all()

    ingredients = []
    bonuses = []
    rares = []
    consumables = []
    potions = []

    for inv in inventory_items:
        item_data = {
            "id": inv.id,
            "item_name": inv.item.name,
            "item_type": inv.item.item_type,
            "rarity": inv.item.rarity,
            "quality": inv.quality if inv.quality else QUALITY_NORMAL,
            "quantity": inv.quantity,
            "description": inv.item.description or "",
            "created_at": format_dt(inv.created_at),
            "icon": inv.item.icon,
        }

        if inv.item.item_type == "ingredient":
            ingredients.append(item_data)
        elif inv.item.item_type == "bonus":
            bonuses.append(item_data)
        elif inv.item.item_type == "rare":
            rares.append(item_data)
        elif inv.item.item_type == "consumable":
            consumables.append(item_data)
        elif inv.item.item_type == "potion":
            potions.append(item_data)

    spark_count = sum(c["quantity"] for c in consumables if c["item_name"] == "Искра Роста")
    player = db.query(Player).filter(Player.id == TEMP_PLAYER_ID).first()

    return templates.TemplateResponse("inventory.html", {
        "request": request,
        "ingredients": ingredients,
        "bonuses": bonuses,
        "rares": rares,
        "consumables": consumables,
        "spark_count": spark_count,
        "total_items": len(inventory_items),
        "coins": player.coins if player else 0,
    })
