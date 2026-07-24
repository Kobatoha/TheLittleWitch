from app.models import Plant, LevelReward
from app.models.player import Player
from app.models.item import Item
from app.models.inventory import Inventory
from app.models.perk import Perk


class TestProfileEndpoints:
    """Тесты профиля и прокачки."""

    def test_profile_page_returns_html(self, client, seeded_db):
        """Страница профиля открывается."""
        response = client.get("/api/game/profile")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_profile_shows_level(self, client, seeded_db):
        """Профиль показывает уровень игрока."""
        response = client.get("/api/game/profile")
        assert response.status_code == 200
        assert "Уровень" in response.text or "level" in response.text.lower()

    def test_profile_shows_coins(self, client, seeded_db):
        """Профиль показывает монеты."""
        response = client.get("/api/game/profile")
        assert response.status_code == 200

    def test_use_potion_levels_up(self, client, seeded_db):
        """Выпить зелье — повысить уровень."""
        # Даём много опыта
        player = seeded_db.query(Player).filter(Player.id == 1).first()
        player.xp_to_next = 100  # мало XP до уровня
        player.experience = 90
        seeded_db.commit()

        # Создаём зелье
        potion = seeded_db.query(Item).filter(Item.item_type == "potion").first()
        if not potion:
            potion = Item(name="Тестовое зелье", item_type="potion", rarity="common")
            seeded_db.add(potion)
            seeded_db.commit()

        inv = Inventory(player_id=1, item_id=potion.id, quantity=1, quality="Обычный")
        seeded_db.add(inv)
        seeded_db.commit()

        # Выпиваем (осуждаю)
        response = client.post("/api/game/inventory/use-potion", json={"inventory_id": inv.id})
        assert response.status_code == 200
        data = response.json()
        assert data["leveled_up"] is True or data["level"] > 1

    def test_use_potion_gives_experience(self, client, seeded_db):
        """Зелье начисляет опыт."""
        potion = seeded_db.query(Item).filter(Item.item_type == "potion").first()
        inv = Inventory(player_id=1, item_id=potion.id, quantity=1, quality="Обычный")
        seeded_db.add(inv)
        seeded_db.commit()

        player_before = seeded_db.query(Player).filter(Player.id == 1).first()
        xp_before = player_before.experience

        response = client.post("/api/game/inventory/use-potion", json={"inventory_id": inv.id})
        assert response.status_code == 200
        data = response.json()
        assert data["experience_gained"] > 0
        assert data["new_experience"] > xp_before

    def test_perk_double_water_works(self, client_with_perks, seeded_db_with_perks):
        """Перк double_water позволяет полить дважды."""
        perks = seeded_db_with_perks.query(Perk).all()
        print(f"Перки в БД: {[(p.perk_code, p.player_id) for p in perks]}")
        # Выдаём перк
        perk = Perk(player_id=1, perk_code="double_water", perk_name="Двойной полив")
        seeded_db_with_perks.add(perk)
        seeded_db_with_perks.commit()

        # Сажаем и поливаем
        plant = seeded_db_with_perks.query(Plant).first()
        r1 = client_with_perks.post("/api/game/garden/plant", json={"plant_id": plant.id})
        bed_id = r1.json()["id"]
        print(f"Посадили, bed_id={bed_id}")

        # Первый полив
        r2 = client_with_perks.post("/api/game/garden/water", json={"bed_id": bed_id})
        print(f"Первый полив: {r2.status_code}, body={r2.text}")
        assert r2.status_code == 200

        # Второй полив с перком — должен работать
        r3 = client_with_perks.post("/api/game/garden/water", json={"bed_id": bed_id})
        print(f"Второй полив: {r3.status_code}, body={r3.text}")
        assert r3.status_code == 200  # перк разрешает

        # Третий полив — заблокирован
        r4 = client_with_perks.post("/api/game/garden/water", json={"bed_id": bed_id})
        assert r4.status_code == 400

    def test_perk_extra_bed_works(self, client_with_perks, seeded_db_with_perks):
        """Перк extra_bed увеличивает лимит грядок."""
        from app.models.perk import Perk
        from app.core import balance

        perk = Perk(player_id=1, perk_code="extra_bed", perk_name="+1 кадка")
        seeded_db_with_perks.add(perk)
        seeded_db_with_perks.commit()

        plant = seeded_db_with_perks.query(Plant).first()
        max_beds = balance.MAX_BEDS_PER_PLAYER + 1  # с перком

        # Сажаем max_beds раз
        for _ in range(max_beds):
            r = client_with_perks.post("/api/game/garden/plant", json={"plant_id": plant.id})
            assert r.status_code == 200

        # Ещё одна — ошибка
        r = client_with_perks.post("/api/game/garden/plant", json={"plant_id": plant.id})
        assert r.status_code == 400

    def test_use_potion_triggers_level_up(self, client_with_perks, seeded_db_with_perks):
        """Выпить зелье — срабатывает левел-ап."""
        player = seeded_db_with_perks.query(Player).filter(Player.id == 1).first()
        player.experience = 90
        player.xp_to_next = 100
        seeded_db_with_perks.commit()

        potion = seeded_db_with_perks.query(Item).filter(Item.item_type == "potion").first()
        inv = Inventory(player_id=1, item_id=potion.id, quantity=1, quality="Обычный")
        seeded_db_with_perks.add(inv)
        seeded_db_with_perks.commit()

        response = client_with_perks.post("/api/game/inventory/use-potion", json={"inventory_id": inv.id})
        assert response.status_code == 200
        data = response.json()
        assert data["leveled_up"] is True
        assert data["level"] == 2

    def test_use_potion_awards_coins_reward(self, client_with_perks, seeded_db_with_perks):
        """Левел-ап с монетной наградой — монеты начислены."""
        lr = LevelReward(level=2, reward_type="coins", reward_name="500 монет", reward_value=500)
        seeded_db_with_perks.add(lr)
        seeded_db_with_perks.commit()

        player = seeded_db_with_perks.query(Player).filter(Player.id == 1).first()
        player.experience = 90
        player.xp_to_next = 100
        coins_before = player.coins
        seeded_db_with_perks.commit()

        potion = seeded_db_with_perks.query(Item).filter(Item.item_type == "potion").first()
        inv = Inventory(player_id=1, item_id=potion.id, quantity=1, quality="Обычный")
        seeded_db_with_perks.add(inv)
        seeded_db_with_perks.commit()

        client_with_perks.post("/api/game/inventory/use-potion", json={"inventory_id": inv.id})

        seeded_db_with_perks.expire_all()
        player_after = seeded_db_with_perks.query(Player).filter(Player.id == 1).first()
        assert player_after.coins > coins_before

    def test_use_potion_awards_title(self, client_with_perks, seeded_db_with_perks):
        """Левел-ап с титулом — титул меняется."""
        lr = LevelReward(level=2, reward_type="title", reward_name="Мастер-травница")
        seeded_db_with_perks.add(lr)
        seeded_db_with_perks.commit()

        player = seeded_db_with_perks.query(Player).filter(Player.id == 1).first()
        player.experience = 90
        player.xp_to_next = 100
        seeded_db_with_perks.commit()

        potion = seeded_db_with_perks.query(Item).filter(Item.item_type == "potion").first()
        inv = Inventory(player_id=1, item_id=potion.id, quantity=1, quality="Обычный")
        seeded_db_with_perks.add(inv)
        seeded_db_with_perks.commit()

        client_with_perks.post("/api/game/inventory/use-potion", json={"inventory_id": inv.id})

        seeded_db_with_perks.expire_all()
        player_after = seeded_db_with_perks.query(Player).filter(Player.id == 1).first()
        assert player_after.title == "Мастер-травница"
