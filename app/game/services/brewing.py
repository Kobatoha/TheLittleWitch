import random

from sqlalchemy.orm import Session

from app.game.services.inventory import add_item_to_inventory

from app.models.inventory import Inventory
from app.models.item import Item
from app.models.recipe import Recipe


def brew_potion(db: Session, player_id: int, recipe_id: int) -> dict:
    """Варит зелье по рецепту. Тратит ингредиенты, возвращает результат."""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise ValueError("Рецепт не найден")

    # Проверяем ингредиенты в инвентаре
    ingredients = []
    for ing_id in [recipe.ingredient_1_id, recipe.ingredient_2_id, recipe.ingredient_3_id]:
        if ing_id:
            inv = db.query(Inventory).filter(
                Inventory.player_id == player_id,
                Inventory.item_id == ing_id,
                Inventory.quantity > 0
            ).first()
            if not inv:
                item = db.query(Item).filter(Item.id == ing_id).first()
                raise ValueError(f"Не хватает: {item.name if item else '???'}")
            ingredients.append(inv)
    
    ingredient_names = []
    for inv in ingredients:
        _ = inv.item.name
        ingredient_names.append(inv.item.name)

    # Считаем шанс успеха с бонусом за качество
    success_chance = recipe.base_success_chance
    quality_bonus = 0
    for inv in ingredients:
        if inv.quality == "Искрящийся":
            quality_bonus += recipe.quality_bonus_percent * 2
        elif inv.quality == "Сочный":
            quality_bonus += recipe.quality_bonus_percent
    success_chance = min(success_chance + quality_bonus, 100)

    # Бросок
    roll = random.uniform(0, 100)
    if roll > success_chance:
        # Неудача — ингредиенты пропадают
        for inv in ingredients:
            inv.quantity -= 1
            if inv.quantity <= 0:
                db.delete(inv)
        db.commit()
        raise ValueError(f"💥 Зелье взорвалось! Шанс был {success_chance:.0f}%, выпало {roll:.0f}%")

    # Успех — тратим ингредиенты, даём зелье
    for inv in ingredients:
        inv.quantity -= 1
        if inv.quantity <= 0:
            db.delete(inv)

    result = add_item_to_inventory(db, player_id, recipe.result_item_id, recipe.result_quantity, "Обычный")
    
    db.commit()
    return {
        "potion_name": recipe.result_item.name,
        "quantity": recipe.result_quantity,
        "success_chance": success_chance,
        "roll": roll,
        "ingredients_used": ingredient_names
    }
    