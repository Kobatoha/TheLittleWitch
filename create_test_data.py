from app.core.database import SessionLocal
from app.models.user import User
from app.models.player import Player

db = SessionLocal()

user = db.query(User).filter(User.username == "test_witch").first()
if not user:
    user = User(
        username="test_witch",
        email="witch@example.com",
        hashed_password="test123",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"User создан: id={user.id}")
else:
    print(f"User уже есть: id={user.id}")

player = db.query(Player).filter(Player.user_id == user.id).first()
if not player:
    player = Player(
        user_id=user.id,
        nickname="Ведьмочка Тест",
        coins=100,
        energy=100,
    )
    db.add(player)
    db.commit()
    db.refresh(player)
    print(f"Player создан: id={player.id}")
else:
    print(f"Player уже есть: id={player.id}")

db.close()
print("Готово!")
