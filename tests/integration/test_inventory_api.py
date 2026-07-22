from app.models.item import Item
from app.models.inventory import Inventory


class TestInventoryEndpoints:
    def test_inventory_page_returns_html(self, client, seeded_db):
        response = client.get("/api/game/inventory")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_empty_inventory_page_works(self, client):
        response = client.get("/api/game/inventory")
        assert response.status_code == 200

    def test_use_potion_success(self, client, seeded_db):
        potion = seeded_db.query(Item).filter(Item.item_type == "potion").first()
        if not potion:
            potion = Item(name="Тестовое зелье", item_type="potion", rarity="common", sell_price=30)
            seeded_db.add(potion)
            seeded_db.commit()

        inv = Inventory(
            player_id=1,
            item_id=potion.id,
            quantity=2,
            quality="Обычный"
        )
        seeded_db.add(inv)
        seeded_db.commit()

        response = client.post("/api/game/inventory/use-potion", json={
            "inventory_id": inv.id
        })
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "experience_gained" in data
        assert data["experience_gained"] > 0

    def test_use_potion_wrong_type_fails(self, client, seeded_db):
        ingredient = seeded_db.query(Item).filter(Item.item_type == "ingredient").first()
        inv = Inventory(
            player_id=1,
            item_id=ingredient.id,
            quantity=1,
            quality="Обычный"
        )
        seeded_db.add(inv)
        seeded_db.commit()

        response = client.post("/api/game/inventory/use-potion", json={
            "inventory_id": inv.id
        })
        assert response.status_code == 400

    def test_use_potion_not_found_fails(self, client):
        response = client.post("/api/game/inventory/use-potion", json={
            "inventory_id": 999
        })
        assert response.status_code == 400

    def test_use_potion_consumes_item(self, client, seeded_db):
        potion = seeded_db.query(Item).filter(Item.item_type == "potion").first()
        inv = Inventory(
            player_id=1,
            item_id=potion.id,
            quantity=1,
            quality="Обычный"
        )
        seeded_db.add(inv)
        seeded_db.commit()

        r1 = client.post("/api/game/inventory/use-potion", json={"inventory_id": inv.id})
        assert r1.status_code == 200

        r2 = client.post("/api/game/inventory/use-potion", json={"inventory_id": inv.id})
        assert r2.status_code == 400

    def test_use_potion_gives_experience(self, client, seeded_db):
        potion = seeded_db.query(Item).filter(Item.item_type == "potion").first()
        inv = Inventory(
            player_id=1,
            item_id=potion.id,
            quantity=1,
            quality="Обычный"
        )
        seeded_db.add(inv)
        seeded_db.commit()

        from app.models.player import Player
        player_before = seeded_db.query(Player).filter(Player.id == 1).first()
        xp_before = player_before.experience

        response = client.post("/api/game/inventory/use-potion", json={"inventory_id": inv.id})
        assert response.status_code == 200

        seeded_db.expire_all()
        player_after = seeded_db.query(Player).filter(Player.id == 1).first()
        assert player_after.experience > xp_before
        