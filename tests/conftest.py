import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.constants import PERK_DOUBLE_WATER, PERK_EXTRA_BED
from app.core.database import Base, get_db
from app.models.recipe import Recipe
from app.models.perk import Perk
from app.models.user import User
from app.models.player import Player
from app.models.plant import Plant
from app.models.item import Item
from app.main import app

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=NullPool  # ← отключаем пул, чтобы не было TimeoutError
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _create_base_data(db):
    # Проверяем, нет ли уже пользователя
    user = db.query(User).filter(User.username == "test").first()
    if not user:
        user = User(username="test", email="test@test.com", hashed_password="test")
        db.add(user)
        db.commit()

    player = db.query(Player).filter(Player.user_id == user.id).first()
    if not player:
        player = Player(user_id=user.id, nickname="TestWitch", coins=500)
        db.add(player)
        db.commit()


    plant = db.query(Plant).filter(Plant.name == "Тестовое растение").first()
    if not plant:
        plant = Plant(
            name="Тестовое растение",
            base_vitality=100, vitality_decay=5,
            essence_per_care=10, growth_per_care=8,
            min_harvest_stage=60, level=1
        )
        db.add(plant)
        db.commit()

    item = db.query(Item).filter(Item.name == "Тестовый ингредиент").first()
    if not item:
        item = Item(name="Тестовый ингредиент", item_type="ingredient", rarity="common", sell_price=10)
        db.add(item)
        db.commit()

    # Зелья
    potion = db.query(Item).filter(Item.name == "Тестовое зелье").first()
    if not potion:
        potion = Item(name="Тестовое зелье", item_type="potion", rarity="common", sell_price=30)
        db.add(potion)
        db.commit()

    ing1 = db.query(Item).filter(Item.name == "Тестовый ингредиент 1").first()
    if not ing1:
        ing1 = Item(name="Тестовый ингредиент 1", item_type="ingredient", rarity="common", sell_price=10)
        db.add(ing1)
        db.commit()

    ing2 = db.query(Item).filter(Item.name == "Тестовый ингредиент 2").first()
    if not ing2:
        ing2 = Item(name="Тестовый ингредиент 2", item_type="ingredient", rarity="common", sell_price=10)
        db.add(ing2)
        db.commit()

    recipe = db.query(Recipe).filter(Recipe.name == "Тестовый рецепт").first()
    if not recipe:
        recipe = Recipe(
            name="Тестовый рецепт", description="Тест",
            ingredient_1_id=ing1.id,
            ingredient_2_id=ing2.id,  # ← РАЗНЫЙ ингредиент
            result_item_id=potion.id,
            result_quantity=1,
            base_success_chance=100.0
        )
        db.add(recipe)
        db.commit()

    seed = db.query(Item).filter(Item.name == f"Семечко {plant.name} ур.1").first()

    if not seed:
        seed = Item(
            name=f"Семечко {plant.name} ур.1",
            item_type="seed",
            rarity="uncommon",
            potency_boost=1,
            linked_plant_id=plant.id
        )
        db.add(seed)
        db.commit()

    return player


@pytest.fixture(scope="function")
def seeded_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    _create_base_data(db)
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def seeded_db_with_perks():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    player = _create_base_data(db)
    if not db.query(Perk).filter(Perk.player_id == player.id, Perk.perk_code == PERK_DOUBLE_WATER).first():
        db.add(Perk(player_id=player.id, perk_code=PERK_DOUBLE_WATER, perk_name="Двойной полив"))
        db.add(Perk(player_id=player.id, perk_code=PERK_EXTRA_BED, perk_name="+1 кадка"))
        db.commit()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(seeded_db):
    def override_get_db():
        yield seeded_db
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client_with_perks(seeded_db_with_perks):
    def override_get_db():
        yield seeded_db_with_perks
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
