import pytest
from pydantic import ValidationError

from app.game.schemas import *


class TestPlantRequest:
    def test_valid_plant_id(self):
        req = PlantRequest(plant_id=1)
        assert req.plant_id == 1

    def test_negative_plant_id_still_works(self):
        req = PlantRequest(plant_id=-5)
        assert req.plant_id == -5

    def test_missing_plant_id_raises_error(self):
        with pytest.raises(ValidationError):
            PlantRequest()

    def test_string_plant_id_raises_error(self):
        with pytest.raises(ValidationError):
            PlantRequest(plant_id="abc")


class TestWaterRequest:
    def test_valid(self):
        req = WaterRequest(bed_id=3)
        assert req.bed_id == 3


class TestHarvestRequest:
    def test_valid(self):
        req = HarvestRequest(bed_id=5)
        assert req.bed_id == 5


class TestUseItemRequest:
    def test_valid(self):
        req = UseItemRequest(bed_id=2)
        assert req.bed_id == 2


class TestCleanRequest:
    def test_valid(self):
        req = CleanRequest(bed_id=1)
        assert req.bed_id == 1


class TestMoonBathRequest:
    def test_valid(self):
        req = MoonBathRequest(bed_id=4)
        assert req.bed_id == 4


class TestGardenBedOut:
    def test_minimal_valid(self):
        bed = GardenBedOut(
            id=1,
            vitality=80,
            essence=50,
            growth_stage=40,
            stage_name="Стебель",
            is_dead=False,
            can_water=True,
            can_harvest=False,
            hours_until_update=12,
        )
        assert bed.plant_name is None
        assert bed.recovery_until is None

    def test_with_all_fields(self):
        bed = GardenBedOut(
            id=1,
            plant_name="Мандрагора",
            vitality=100,
            essence=120,
            growth_stage=60,
            stage_name="Бутон",
            is_dead=False,
            can_water=True,
            can_harvest=True,
            recovery_until="22.07.2026 15:00",
            recovery_until_str="22.07.2026 15:00",
            hours_until_update=8,
            planted_at="20.07.2026 10:00",
        )
        assert bed.plant_name == "Мандрагора"


class TestWaterResultOut:
    def test_valid(self):
        result = WaterResultOut(
            plant_name="Лунная лилия",
            vitality=85,
            essence=60,
            growth_stage=40,
            stage_name="Стебель",
        )
        assert result.ok is True


class TestHarvestResultOut:
    def test_valid_empty_lists(self):
        result = HarvestResultOut(
            plant_name="Мандрагора",
            stage="Цветение",
            main_harvest=[],
            bonus_harvest=[],
            rare_harvest=[],
        )
        assert result.ok is True

    def test_valid_with_items(self):
        result = HarvestResultOut(
            plant_name="Мандрагора",
            stage="Цветение",
            main_harvest=[{"name": "Корень мандрагоры", "quantity": 2, "quality": "Сочный"}],
            bonus_harvest=[{"name": "Капля росы", "rarity": "common"}],
            rare_harvest=[],
        )
        assert len(result.main_harvest) == 1


class TestSparkResultOut:
    def test_valid(self):
        result = SparkResultOut(
            plant_name="Шипучка",
            growth_stage=50,
            stage_name="Стебель",
            essence=40,
            can_water=True,
        )
        assert result.ok is True


class TestCleanResultOut:
    def test_valid(self):
        result = CleanResultOut(
            plant_name="Мандрагора",
            vitality=90,
            essence=55,
        )
        assert result.ok is True


class TestMoonBathResultOut:
    def test_valid_minimal(self):
        result = MoonBathResultOut(
            plant_name="Лунная лилия",
            vitality=95,
            essence=70,
        )
        assert result.moon_phase == ""
        assert result.bonus == 0


class TestInventoryItemOut:
    def test_valid(self):
        item = InventoryItemOut(
            id=1,
            item_name="Капля росы",
            item_type="bonus",
            rarity="common",
            quality="Обычный",
            quantity=3,
            description="Чистая влага.",
        )
        assert item.item_name == "Капля росы"
        assert item.created_at is None
