from app.models.item import Item
from app.models.player import Player
from app.models.inventory import Inventory


class TestShopEndpoints:
    def test_shop_page_returns_html(self, client, seeded_db):
        response = client.get("/api/game/shop")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_sell_item_success(self, client, seeded_db):
        item = seeded_db.query(Item).first()
        inv = Inventory(
            player_id=1,
            item_id=item.id,
            quantity=5,
            quality="Обычный"
        )
        seeded_db.add(inv)
        seeded_db.commit()

        player_before = seeded_db.query(Player).filter(Player.id == 1).first()
        coins_before = player_before.coins

        response = client.post("/api/game/shop/sell", json={
            "inventory_id": inv.id,
            "quantity": 2
        })
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["quantity_sold"] == 2
        assert data["total_coins_earned"] > 0

        seeded_db.expire_all()
        player_after = seeded_db.query(Player).filter(Player.id == 1).first()
        assert player_after.coins > coins_before

    def test_sell_more_than_have_fails(self, client, seeded_db):
        item = seeded_db.query(Item).first()
        inv = Inventory(
            player_id=1,
            item_id=item.id,
            quantity=1,
            quality="Обычный"
        )
        seeded_db.add(inv)
        seeded_db.commit()

        response = client.post("/api/game/shop/sell", json={
            "inventory_id": inv.id,
            "quantity": 10
        })
        assert response.status_code == 400

    def test_sell_nonexistent_fails(self, client):
        response = client.post("/api/game/shop/sell", json={
            "inventory_id": 999,
            "quantity": 1
        })
        assert response.status_code == 400

    def test_sell_all_removes_item(self, client, seeded_db):
        item = seeded_db.query(Item).first()
        inv = Inventory(
            player_id=1,
            item_id=item.id,
            quantity=3,
            quality="Обычный"
        )
        seeded_db.add(inv)
        seeded_db.commit()

        response = client.post("/api/game/shop/sell", json={
            "inventory_id": inv.id,
            "quantity": 3
        })
        assert response.status_code == 200
        data = response.json()
        assert data["remaining_quantity"] == 0

    def test_sell_partial_leaves_remainder(self, client, seeded_db):
        item = seeded_db.query(Item).first()
        inv = Inventory(
            player_id=1,
            item_id=item.id,
            quantity=5,
            quality="Обычный"
        )
        seeded_db.add(inv)
        seeded_db.commit()

        response = client.post("/api/game/shop/sell", json={
            "inventory_id": inv.id,
            "quantity": 2
        })
        assert response.status_code == 200
        data = response.json()
        assert data["remaining_quantity"] == 3
        