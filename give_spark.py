from app.core.config import QUALITY_NORMAL, TEMP_PLAYER_ID
from app.core.database import SessionLocal
from app.models.item import Item
from app.models.inventory import Inventory

db = SessionLocal()

spark = db.query(Item).filter(Item.name == "Искра Роста").first()
if not spark:
    print("❌ Предмет не найден. Запусти python -m app.game.seed_items")
else:
    inv = Inventory(player_id=TEMP_PLAYER_ID, item_id=spark.id, quantity=5, quality=QUALITY_NORMAL)
    db.add(inv)
    db.commit()
    print(f"✅ Выдано 5x Искра Роста игроку 1")

db.close()
