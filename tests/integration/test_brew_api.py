from app.models.recipe import Recipe
from app.models.item import Item
from app.models.inventory import Inventory


class TestBrewEndpoints:
    def test_brew_page_returns_html(self, client, seeded_db):
        response = client.get("/api/game/brew")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_brew_without_ingredients_fails(self, client, seeded_db):
        recipe = seeded_db.query(Recipe).first()
        
        response = client.post("/api/game/brew", json={
            "recipe_id": recipe.id
        })
        assert response.status_code == 400

    def test_brew_with_ingredients_success(self, client, seeded_db):
        recipe = seeded_db.query(Recipe).first()
        
        # Выдаём игроку нужные ингредиенты
        for ing_id in [recipe.ingredient_1_id, recipe.ingredient_2_id]:
            if ing_id:
                inv = Inventory(
                    player_id=1,
                    item_id=ing_id,
                    quantity=3,
                    quality="Обычный"
                )
                seeded_db.add(inv)
        seeded_db.commit()
        
        response = client.post("/api/game/brew", json={
            "recipe_id": recipe.id
        })
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "potion_name" in data

    def test_invalid_recipe_fails(self, client):
        response = client.post("/api/game/brew", json={
            "recipe_id": 999
        })
        assert response.status_code == 400

    def test_missing_recipe_id_fails(self, client):
        response = client.post("/api/game/brew", json={})
        assert response.status_code == 422

    def test_potion_appears_in_inventory_after_brew(self, client, seeded_db):
        recipe = seeded_db.query(Recipe).first()

        for ing_id in [recipe.ingredient_1_id, recipe.ingredient_2_id]:
            if ing_id:
                inv = Inventory(
                    player_id=1,
                    item_id=ing_id,
                    quantity=3,
                    quality="Обычный"
                )
                seeded_db.add(inv)
        seeded_db.commit()

        client.post("/api/game/brew", json={"recipe_id": recipe.id})

        response = client.get("/api/game/inventory")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_ingredients_consumed_after_brew(self, client, seeded_db):
        recipe = seeded_db.query(Recipe).first()

        for ing_id in [recipe.ingredient_1_id, recipe.ingredient_2_id]:
            if ing_id:
                inv = Inventory(
                    player_id=1,
                    item_id=ing_id,
                    quantity=1,
                    quality="Обычный"
                )
                seeded_db.add(inv)
        seeded_db.commit()

        response1 = client.post("/api/game/brew", json={"recipe_id": recipe.id})
        assert response1.status_code == 200

        response2 = client.post("/api/game/brew", json={"recipe_id": recipe.id})
        assert response2.status_code == 400
