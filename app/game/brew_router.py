from pathlib import Path
from pydantic import BaseModel
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.database import get_db
from app.core import config

from app.game import services
from app.game.router import format_dt

from app.models.item import Item
from app.models.inventory import Inventory
from app.models.recipe import Recipe
from app.models.player import Player

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


class BrewRequest(BaseModel):
    recipe_id: int


@router.post("/brew")
def brew_potion(request: BrewRequest, db: Session = Depends(get_db)):
    try:
        result = services.brew_potion(db, config.TEMP_PLAYER_ID, request.recipe_id)
        return {"ok": True, **result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/brew", response_class=HTMLResponse)
def brew_page(request: Request, db: Session = Depends(get_db)):
    recipes = db.query(Recipe).all()
    player = db.query(Player).filter(Player.id == config.TEMP_PLAYER_ID).first()
    
    # Соберём рецепты с информацией о наличии ингредиентов
    recipes_data = []
    for r in recipes:
        ing1 = db.query(Inventory).filter(
            Inventory.player_id == config.TEMP_PLAYER_ID,
            Inventory.item_id == r.ingredient_1_id,
            Inventory.quantity > 0
        ).first()
        ing2 = db.query(Inventory).filter(
            Inventory.player_id == config.TEMP_PLAYER_ID,
            Inventory.item_id == r.ingredient_2_id,
            Inventory.quantity > 0
        ).first() if r.ingredient_2_id else None
        ing3 = db.query(Inventory).filter(
            Inventory.player_id == config.TEMP_PLAYER_ID,
            Inventory.item_id == r.ingredient_3_id,
            Inventory.quantity > 0
        ).first() if r.ingredient_3_id else None
        
        can_brew = ing1 is not None
        if r.ingredient_2_id and not ing2:
            can_brew = False
        if r.ingredient_3_id and not ing3:
            can_brew = False
        
        recipes_data.append({
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "ingredient_1_name": r.ingredient_1.name if r.ingredient_1 else "?",
            "ingredient_2_name": r.ingredient_2.name if r.ingredient_2 else None,
            "ingredient_3_name": r.ingredient_3.name if r.ingredient_3 else None,
            "result_name": r.result_item.name if r.result_item else "?",
            "success_chance": r.base_success_chance,
            "can_brew": can_brew,
            "ing1_quality": ing1.quality if ing1 else None,
            "ing2_quality": ing2.quality if ing2 else None,
        })

    spark_count = 0
    spark_item = db.query(Item).filter(Item.name == "Искра Роста").first()
    if spark_item:
        spark_inv = db.query(Inventory).filter(
            Inventory.player_id == config.TEMP_PLAYER_ID,
            Inventory.item_id == spark_item.id
        ).first()
        if spark_inv:
            spark_count = spark_inv.quantity

    return templates.TemplateResponse("brew.html", {
        "request": request,
        "recipes": recipes_data,
        "spark_count": spark_count,
        "coins": player.coins if player else 0
    })
