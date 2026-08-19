from app.core.database import SessionLocal
from app.game.services.inventory import add_item_to_inventory
from app.models.item import Item

def give_starter_seeds():
    db = SessionLocal()

    # Ищем семечки 1-го уровня
    seeds = db.query(Item).filter(Item.item_type == "seed", Item.potency_boost == 1).all()

    if not seeds:
        print("❌ Семечек нет в БД. Сначала собери урожай или создай их.")
        db.close()
        return

    for seed in seeds:
        add_item_to_inventory(db, player_id=1, item_id=seed.id, quantity=3, quality="Обычный")
        print(f"✅ Выдано 3x {seed.name}")

    db.close()
    print("Готово!")

if __name__ == "__main__":
    give_starter_seeds()
