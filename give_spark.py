from app.core.database import SessionLocal
from app.game.services import add_item_to_inventory
from app.models.item import Item

db = SessionLocal()

spark = db.query(Item).filter(Item.name == "Искра Роста").first()
if not spark:
    print("❌ Предмет не найден. Запусти python -m app.game.seed_items")
else:
    # Ищем, кому выдать (первый попавшийся игрок)
    add_item_to_inventory(db, player_id=1, item_id=spark.id, quantity=5, quality="Обычный")
    print(f"✅ Выдано 5x Искра Роста игроку 1 (суммируется с существующими)")

db.close()