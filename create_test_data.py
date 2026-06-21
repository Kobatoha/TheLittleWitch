from app.core.database import SessionLocal
from app.models.user import User
from app.models.player import Player

db = SessionLocal()

# Создаём пользователя
user = User(
    username="test_witch",
    email="witch@example.com",
    hashed_password="test123",  # потом заменим на нормальный хэш
    is_active=True,
)
db.add(user)
db.commit()
db.refresh(user)
print(f"User создан: id={user.id}, username={user.username}")

# Создаём игрока (ведьмочку)
player = Player(
    user_id=user.id,
    nickname="Ведьмочка Тест",
    coins=100,
    energy=100,
)
db.add(player)
db.commit()
db.refresh(player)
print(f"Player создан: id={player.id}, nickname={player.nickname}")

db.close()
print("Готово!")
