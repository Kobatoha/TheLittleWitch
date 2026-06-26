from pathlib import Path

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.core.database import get_db
from app.core import config
from app.game import services
from app.game.router import format_dt
from app.models.player import Player

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


class SellRequest(BaseModel):
    inventory_id: int
    quantity: int = 1


@router.post("/shop/sell")
def sell_item(request: SellRequest, db: Session = Depends(get_db)):
    try:
        result = services.sell_item(db, config.TEMP_PLAYER_ID, request.inventory_id, request.quantity)
        return {"ok": True, **result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/shop", response_class=HTMLResponse)
def shop_page(request: Request, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.id == config.TEMP_PLAYER_ID).first()
    shop_items = services.get_player_items_for_shop(db, config.TEMP_PLAYER_ID)

    items_data = []
    for inv in shop_items:
        items_data.append({
            "id": inv.id,
            "item_name": inv.item.name,
            "item_type": inv.item.item_type,
            "rarity": inv.item.rarity,
            "quality": inv.quality if inv.quality else "Обычный",
            "quantity": inv.quantity,
            "sell_price": inv.item.sell_price,
            "description": inv.item.description or "",
        })

    return templates.TemplateResponse("shop.html", {
        "request": request,
        "coins": player.coins if player else 0,
        "items": items_data,
        "total_items": len(items_data)
    })
    