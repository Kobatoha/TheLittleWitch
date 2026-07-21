from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.item import Item
from app.models.player import Player


def add_item_to_inventory(db: Session, player_id: int, item_id: int, quantity: int = 1, quality: str = "Обычный", source_bed_id: int = None) -> Inventory:
    """Добавляет предмет в инвентарь. Если такой же уже есть — увеличивает количество."""
    existing = db.query(Inventory).filter(
        Inventory.player_id == player_id,
        Inventory.item_id == item_id,
        Inventory.quality == quality
    ).first()

    if existing:
        existing.quantity += quantity
        db.commit()
        return existing
    else:
        inv = Inventory(
            player_id=player_id,
            item_id=item_id,
            quantity=quantity,
            quality=quality,
            source_bed_id=source_bed_id
        )
        db.add(inv)
        db.commit()
        db.refresh(inv)
        return inv

def sell_item(db: Session, player_id: int, inventory_id: int, sell_quantity: int = 1) -> dict:
    """Продаёт предмет из инвентаря. Возвращает результат."""
    inv = db.query(Inventory).filter(
        Inventory.id == inventory_id,
        Inventory.player_id == player_id,
        Inventory.quantity > 0
    ).first()
    if not inv:
        raise ValueError("Предмет не найден в инвентаре")
    if sell_quantity > inv.quantity:
        raise ValueError(f"Недостаточно предметов! У тебя {inv.quantity} шт.")

    item = inv.item
    total_price = item.sell_price * sell_quantity

    # === БОНУС К ЦЕНЕ ЗА ПЕРК ===
    if has_perk(db, player_id, "market_bonus_20"):
        total_price = int(total_price * 1.2)

    # Списываем предмет
    inv.quantity -= sell_quantity
    if inv.quantity <= 0:
        db.delete(inv)

    # Добавляем монеты игроку
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise ValueError("Игрок не найден")
    player.coins += total_price

    db.commit()

    return {
        "item_name": item.name,
        "quantity_sold": sell_quantity,
        "price_per_item": item.sell_price,
        "total_coins_earned": total_price,
        "coins_now": player.coins,
        "remaining_quantity": inv.quantity if inv.quantity > 0 else 0
    }


def get_player_items_for_shop(db: Session, player_id: int) -> list:
    """Возвращает все предметы игрока для отображения в магазине."""
    items = db.query(Inventory).filter(
        Inventory.player_id == player_id,
        Inventory.quantity > 0
    ).order_by(Inventory.item.has(Item.item_type == "rare").desc(),
               Inventory.item.has(Item.sell_price).desc()).all()
    return items
