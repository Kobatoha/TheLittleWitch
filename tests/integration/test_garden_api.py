import pytest

from app.models.plant import Plant
from app.models.user import User
from app.models.player import Player


class TestGardenEndpoints:
    def test_get_garden_empty(self, client):
        response = client.get("/api/game/garden")
        assert response.status_code == 200
        assert response.json() == []

    def test_plant_seed_success(self, client, seeded_db):
        plant = seeded_db.query(Plant).first()
        
        response = client.post("/api/game/garden/plant", json={
            "plant_id": plant.id
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["plant_name"] == plant.name
        assert data["growth_stage"] == 0
        assert data["stage_name"] == "Семя"
        assert data["is_dead"] is False

    def test_plant_seed_invalid_id(self, client):
        response = client.post("/api/game/garden/plant", json={
            "plant_id": 999
        })
        assert response.status_code == 400

    def test_get_garden_after_planting(self, client, seeded_db):
        plant = seeded_db.query(Plant).first()

        client.post("/api/game/garden/plant", json={"plant_id": plant.id})

        response = client.get("/api/game/garden")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["plant_name"] == plant.name

    def test_water_bed_success(self, client, seeded_db):
        plant = seeded_db.query(Plant).first()
        
        plant_resp = client.post("/api/game/garden/plant", json={"plant_id": plant.id})
        bed_id = plant_resp.json()["id"]

        response = client.post("/api/game/garden/water", json={"bed_id": bed_id})
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["essence"] > 0

    def test_water_empty_bed_fails(self, client):
        response = client.post("/api/game/garden/water", json={"bed_id": 1})
        assert response.status_code == 400

    def test_double_water_blocked(self, client, seeded_db):
        plant = seeded_db.query(Plant).first()
        
        plant_resp = client.post("/api/game/garden/plant", json={"plant_id": plant.id})
        bed_id = plant_resp.json()["id"]

        r1 = client.post("/api/game/garden/water", json={"bed_id": bed_id})
        assert r1.status_code == 200

        r2 = client.post("/api/game/garden/water", json={"bed_id": bed_id})
        assert r2.status_code == 400

    def test_clean_bed_success(self, client, seeded_db):
        plant = seeded_db.query(Plant).first()
        
        plant_resp = client.post("/api/game/garden/plant", json={"plant_id": plant.id})
        bed_id = plant_resp.json()["id"]
        
        response = client.post("/api/game/garden/clean", json={"bed_id": bed_id})
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True

    def test_plant_limit_respected(self, client, seeded_db):
        plant = seeded_db.query(Plant).first()

        for _ in range(4):
            resp = client.post("/api/game/garden/plant", json={"plant_id": plant.id})
            assert resp.status_code == 200

        resp = client.post("/api/game/garden/plant", json={"plant_id": plant.id})
        assert resp.status_code == 400

    def test_harvest_requires_growth(self, client, seeded_db):
        plant = seeded_db.query(Plant).first()
        
        plant_resp = client.post("/api/game/garden/plant", json={"plant_id": plant.id})
        bed_id = plant_resp.json()["id"]

        response = client.post("/api/game/garden/harvest", json={"bed_id": bed_id})
        assert response.status_code == 400

    def test_moon_bath_success(self, client, seeded_db):
        plant = seeded_db.query(Plant).first()
        
        plant_resp = client.post("/api/game/garden/plant", json={"plant_id": plant.id})
        bed_id = plant_resp.json()["id"]
        
        response = client.post("/api/game/garden/moon-bath", json={"bed_id": bed_id})
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True

    def test_page_returns_html(self, client, seeded_db):
        response = client.get("/api/game/garden/page")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
