from datetime import datetime, timedelta

from app.core.constants import ITEM_GROWTH_SPARK
from app.models import GardenBed
from app.models.plant import Plant
from app.models.user import User
from app.models.player import Player
from app.models.inventory import Inventory
from app.models.item import Item


class TestGardenEndpoints:
    def test_get_garden_empty(self, client, seeded_db):
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

    def test_plant_seed_invalid_id(self, client, seeded_db):
        response = client.post("/api/game/garden/plant", json={
            "plant_id": 999
        })
        assert response.status_code == 404

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

    def test_water_empty_bed_fails(self, client, seeded_db):
        response = client.post("/api/game/garden/water", json={"bed_id": 1})
        assert response.status_code == 404

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

    def test_moon_bath_increases_stat(self, client, seeded_db):
        """После лунной ванны счётчик увеличивается."""
        plant = seeded_db.query(Plant).first()
        r = client.post("/api/game/garden/plant", json={"plant_id": plant.id})
        bed_id = r.json()["id"]

        player_before = seeded_db.query(Player).filter(Player.id == 1).first()
        baths_before = player_before.total_moon_baths

        client.post("/api/game/garden/moon-bath", json={"bed_id": bed_id})

        seeded_db.expire_all()
        player_after = seeded_db.query(Player).filter(Player.id == 1).first()
        assert player_after.total_moon_baths == baths_before + 1

    def test_page_returns_html(self, client, seeded_db):
        response = client.get("/api/game/garden/page")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_harvest_success_after_growth(self, client, seeded_db):
        plant = seeded_db.query(Plant).first()

        seed_plant = client.post("/api/game/garden/plant", json={"plant_id": plant.id})
        bed_id = seed_plant.json()["id"]

        bed = seeded_db.query(GardenBed).filter(GardenBed.id == bed_id).first()
        bed.growth_stage = 80
        seeded_db.commit()

        response = client.post("/api/game/garden/harvest", json={"bed_id": bed_id})
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert len(data["main_harvest"]) > 0

    def test_harvest_increases_harvest_stat(self, client, seeded_db):
        """После сбора счётчик урожаев увеличивается."""
        plant = seeded_db.query(Plant).first()
        r = client.post("/api/game/garden/plant", json={"plant_id": plant.id})
        bed_id = r.json()["id"]

        bed = seeded_db.query(GardenBed).filter(GardenBed.id == bed_id).first()
        bed.growth_stage = 80
        seeded_db.commit()

        player_before = seeded_db.query(Player).filter(Player.id == 1).first()
        harvests_before = player_before.total_harvests

        client.post("/api/game/garden/harvest", json={"bed_id": bed_id})

        seeded_db.expire_all()
        player_after = seeded_db.query(Player).filter(Player.id == 1).first()
        assert player_after.total_harvests == harvests_before + 1

    def test_harvest_resets_essence(self, client, seeded_db):
        plant = seeded_db.query(Plant).first()
        seed_plant = client.post("api/game/garden/plant", json={"plant_id": plant.id})
        bed_id = seed_plant.json()["id"]

        bed = seeded_db.query(GardenBed).filter(GardenBed.id == bed_id).first()
        bed.growth_stage = 80
        bed.essence = 150
        seeded_db.commit()

        client.post("api/game/garden/harvest", json={"bed_id": bed_id})

        seeded_db.expire_all()
        bed_after = seeded_db.query(GardenBed).filter(GardenBed.id == bed_id).first()
        assert bed_after.essence == 0

    def test_harvest_reduces_vitality(self, client, seeded_db):
        plant = seeded_db.query(Plant).first()
        seed_plant = client.post("api/game/garden/plant", json={"plant_id": plant.id})
        bed_id = seed_plant.json()["id"]

        bed = seeded_db.query(GardenBed).filter(GardenBed.id == bed_id).first()
        bed.growth_stage = 80
        bed.vitality = 100
        seeded_db.commit()

        client.post("api/game/garden/harvest", json={"bed_id": bed_id})

        seeded_db.expire_all()
        bed_after = seeded_db.query(GardenBed).filter(GardenBed.id == bed_id).first()
        assert bed_after.essence < 100

    def test_daily_update_advances_growth(self, client, seeded_db):
        plant = seeded_db.query(Plant).first()
        seed_plant = client.post("api/game/garden/plant", json={"plant_id": plant.id})
        bed_id = seed_plant.json()["id"]

        bed = seeded_db.query(GardenBed).filter(GardenBed.id == bed_id).first()
        original_stage = bed.growth_stage
        bed.last_daily_update = datetime.utcnow() - timedelta(hours=25)
        seeded_db.commit()

        client.get("/api/game/garden/page")

        seeded_db.expire_all()
        bed_after = seeded_db.query(GardenBed).filter(GardenBed.id == bed_id).first()
        assert bed_after.growth_stage > original_stage

    def test_daily_update_reduces_vitality(self, client, seeded_db):
        plant = seeded_db.query(Plant).first()
        seed_plant = client.post("api/game/garden/plant", json={"plant_id": plant.id})
        bed_id = seed_plant.json()["id"]

        bed = seeded_db.query(GardenBed).filter(GardenBed.id == bed_id).first()
        bed.vitality = 100
        bed.last_daily_update = datetime.utcnow() - timedelta(hours=25)
        seeded_db.commit()

        client.get("/api/game/garden/page")

        seeded_db.expire_all()
        bed_after = seeded_db.query(GardenBed).filter(GardenBed.id == bed_id).first()
        assert bed_after.vitality < 100

    def test_use_spark_advances_growth(self, client, seeded_db):
        plant = seeded_db.query(Plant).first()
        seed_plant = client.post("api/game/garden/plant", json={"plant_id": plant.id})
        bed_id = seed_plant.json()["id"]

        spark = seeded_db.query(Item).filter(Item.name == ITEM_GROWTH_SPARK).first()
        if not spark:
            spark = Item(name=ITEM_GROWTH_SPARK, item_type="consumable", rarity="uncommon")
            seeded_db.add(spark)
            seeded_db.commit()

        seeded_db.add(Inventory(player_id=1, item_id=spark.id, quantity=5, quality="Обычный"))
        seeded_db.commit()

        bed = seeded_db.query(GardenBed).filter(GardenBed.id == bed_id).first()
        original_stage = bed.growth_stage

        response = client.post("/api/game/garden/use-spark", json={"bed_id": bed_id})
        assert response.status_code == 200

        seeded_db.expire_all()
        bed_after = seeded_db.query(GardenBed).filter(GardenBed.id == bed_id).first()
        assert bed_after.growth_stage > original_stage
