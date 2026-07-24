import pytest

from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _create_base_data(db):
    """Создаёт базовые данные (игрок, растение, предметы, рецепт)."""
    user = User(username="test", email="test@test.com", hashed_password="test")
    db.add(user)
    db.commit()

    player = Player(user_id=user.id, nickname="TestWitch", coins=500)
    db.add(player)
    db.commit()

    plant = Plant(
        name="Тестовое растение",
        base_vitality=100, vitality_decay=5,
        essence_per_care=10, growth_per_care=8,
        min_harvest_stage=60, base_potency=100
    )
    db.add(plant)
    db.commit()

    item = Item(name="Тестовый ингредиент", item_type="ingredient", rarity="common", sell_price=10)
    db.add(item)
    db.commit()

    ingredient1 = Item(name="Тестовый ингредиент 1", item_type="ingredient", rarity="common", sell_price=10)
    ingredient2 = Item(name="Тестовый ингредиент 2", item_type="ingredient", rarity="common", sell_price=10)
    potion_item = Item(name="Тестовое зелье", item_type="potion", rarity="common", sell_price=30)
    db.add_all([ingredient1, ingredient2, potion_item])
    db.commit()

    recipe = Recipe(
        name="Тестовый рецепт", description="Тест",
        ingredient_1_id=ingredient1.id, ingredient_2_id=ingredient2.id,
        result_item_id=potion_item.id, result_quantity=1,
        base_success_chance=100.0, quality_bonus_percent=0
    )
    db.add(recipe)
    db.commit()

    return player


@pytest.fixture(scope="function")
def seeded_db():
    """БД с базовыми данными (без перков)."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    _create_base_data(db)
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def seeded_db_with_perks():
    """БД с базовыми данными + перки."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    player = _create_base_data(db)
    db.add(Perk(player_id=player.id, perk_code=PERK_DOUBLE_WATER, perk_name="Двойной полив"))
    db.add(Perk(player_id=player.id, perk_code=PERK_EXTRA_BED, perk_name="+1 кадка"))
    db.commit()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(seeded_db):
    """Тестовый клиент с seeded_db (без перков)."""
    def override_get_db():
        yield seeded_db
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client_with_perks(seeded_db_with_perks):
    """Тестовый клиент с seeded_db_with_perks."""
    def override_get_db():
        yield seeded_db_with_perks
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
