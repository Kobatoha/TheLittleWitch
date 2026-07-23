import random
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.core import balance
from app.core.constants import ACTION_WATER, PERK_DOUBLE_WATER, PERK_STRONG_CLEAN, ACTION_MOON, ITEM_GROWTH_SPARK, \
    ACTION_SPARK, PERK_RARE_LUCK_10, ACTION_HARVEST, ACTION_DAILY
from app.core.exceptions import GameError, ErrorCode

from app.game import formulas
from app.game.utils import format_dt
from app.game.moon import get_essence_bonus_for_night, get_moon_phase
from app.game.services.logging import log_action
from app.game.services.profile import has_perk, get_max_beds
from app.game.services.inventory import add_item_to_inventory

from app.models.garden_bed import GardenBed
from app.models.inventory import Inventory
from app.models.item import Item
from app.models.plant import Plant
from app.models.player import Player
from app.models.care_log import CareLog


class GardenService:
    def __init__(self, db: Session, player_id: int):
        self.db = db
        self.player_id = player_id

        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise GameError(ErrorCode.PLAYER_NOT_FOUND)
        self.player = player

    def _get_bed(self, bed_id: int) -> GardenBed:
        bed = self.db.query(GardenBed).filter(
            GardenBed.id == bed_id,
            GardenBed.player_id == self.player_id
        ).first()
        if not bed:
            raise GameError(ErrorCode.BED_NOT_FOUND)
        if bed.plant_id is None:
            raise GameError(ErrorCode.PLANT_NOT_FOUND)
        return bed

    def _get_living_bed(self, bed_id: int) -> GardenBed:
        bed = self._get_bed(bed_id)
        if bed.is_dead:
            raise GameError(ErrorCode.PLANT_DEAD)
        return bed

    def get_player_garden(self) -> list[type[GardenBed]]:
        return self.db.query(GardenBed).filter(
            GardenBed.player_id == self.player_id
        ).all()

    def plant_seed(self, plant_id: int) -> GardenBed:
        max_beds = get_max_beds(self.db, self.player_id)
        beds_count = self.db.query(GardenBed).filter(
            GardenBed.player_id == self.player_id,
            GardenBed.plant_id != None
        ).count()
        if beds_count >= max_beds:
            raise GameError(ErrorCode.MAX_BEDS_REACHED)

        plant = self.db.query(Plant).filter(Plant.id == plant_id).first()
        if not plant:
            raise GameError(ErrorCode.PLANT_NOT_FOUND)

        bed = self.db.query(GardenBed).filter(
            GardenBed.player_id == self.player_id,
            GardenBed.plant_id == None
        ).first()
        if not bed:
            bed = GardenBed(player_id=self.player_id)

        bed.plant_id = plant_id
        bed.vitality = plant.base_vitality
        bed.essence = 0
        bed.growth_stage = 0
        bed.planted_at = datetime.utcnow()

        self.db.add(bed)
        self.db.commit()
        self.db.refresh(bed)
        return bed

    def water_bed(self, bed_id: int) -> GardenBed:
        bed = self._get_living_bed(bed_id)

        if not bed.can_water:
            raise GameError(ErrorCode.WATER_ALREADY_USED)

        plant = bed.plant

        bed.vitality = min(bed.vitality + balance.WATER_VITALITY_BOOST, max(plant.base_vitality, 100))
        bed.essence += plant.essence_per_care
        bed.growth_stage = min(bed.growth_stage, 100)
        bed.last_watered_at = datetime.utcnow()

        log_action(self.db, self.player_id, bed.id, "water",
        "Орошение лунной росой",
        f"❤️+{balance.WATER_VITALITY_BOOST}% ✨+{plant.essence_per_care}",
        "positive")

        self.db.commit()
        self.db.refresh(bed)
        return bed

    def can_water_bed(self, bed: GardenBed) -> bool:
        if bed.is_dead or bed.plant_id is None:
            return False
        if bed.recovery_until and bed.recovery_until > datetime.utcnow():
            return False
        if bed.last_watered_at:
            if has_perk(self.db, self.player_id, PERK_DOUBLE_WATER):
                today_count = self.db.query(CareLog).filter(
                    CareLog.garden_bed_id == bed.id,
                    CareLog.action == ACTION_WATER,
                    CareLog.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
                ).count()
                if today_count >= 2:
                    return False
            else:
                if bed.last_watered_at.date() >= datetime.utcnow().date():
                    return False
        return True

    def clean_bed(self, bed_id: int) -> GardenBed:
        bed = self._get_living_bed(bed_id)

        if bed.last_cleaned_at and bed.last_cleaned_at.date() >= datetime.utcnow().date():
            raise GameError(ErrorCode.CLEAN_ALREADY_USED)

        plant = bed.plant

        vitality_boost = 10 if has_perk(self.db, self.player_id, PERK_STRONG_CLEAN) else 5
        bed.vitality = min(bed.vitality + vitality_boost, max(plant.base_vitality, 100))
        bed.essence += 2
        bed.last_cleaned_at = datetime.utcnow()

        details = None
        if random.random() < 0.2:
            findings = ["радужный пучеглаз", "сонная божья коровка", "крошка лунного камня", "пёрышко звёздной птицы"]
            details = f"Найден(а) {random.choice(findings)}!"

        log_action(self.db, self.player_id, bed.id, "clean",
            "Очищение листьев",
            f"❤️+{vitality_boost}% ✨+2",
            "positive", details)

        self.db.commit()
        self.db.refresh(bed)
        return bed
 
    def moon_bath(self, bed_id: int) -> GardenBed:
        bed = self._get_living_bed(bed_id)

        if bed.last_moon_bath_at and bed.last_moon_bath_at.date() >= datetime.utcnow().date():
            raise GameError(ErrorCode.MOON_BATH_ALREADY_USED)

        moon = get_moon_phase()
        bonus = moon["essence_bonus"]

        if bonus == 0:
            raise GameError(ErrorCode.MOON_TOO_WEAK)

        plant = bed.plant
        vitality_bonus = bonus // 2
        bed.vitality = min(bed.vitality + vitality_bonus, max(plant.base_vitality, 100))
        bed.essence += bonus
        bed.last_moon_bath_at = datetime.utcnow()

        log_action(self.db, self.player_id, bed.id, ACTION_MOON,
        f"Лунная ванна ({moon['name']})",
        f"❤️+{vitality_bonus}% ✨+{bonus}",
        "positive" if bonus >= 10 else "neutral")

        self.db.commit()
        self.db.refresh(bed)
        return bed

    def use_growth_spark(self, bed_id: int) -> GardenBed:
        bed = self._get_living_bed(bed_id)
        if bed.growth_stage >= 100:
            raise ValueError("Растение уже в Зрелости!")

        spark_item = self.db.query(Item).filter(Item.name == ITEM_GROWTH_SPARK).first()
        if not spark_item:
            raise GameError(ErrorCode.SPARK_ITEM_NOT_FOUND)

        inv = self.db.query(Inventory).filter(
            Inventory.player_id == self.player_id,
            Inventory.item_id == spark_item.id,
            Inventory.quantity > 0
        ).first()
        if not inv:
            raise GameError(ErrorCode.NO_GROWTH_SPARK)

        inv.quantity -= 1
        if inv.quantity <= 0:
            self.db.delete(inv)

        bed.last_watered_at = None
        bed.last_cleaned_at = None
        bed.recovery_until = None
        bed.last_moon_bath_at = None

        bed.growth_stage = min(bed.growth_stage + balance.SPARK_GROWTH_PERCENT, 100)
        bed.vitality = max(bed.vitality - balance.SPARK_VITALITY_COST, 0)

        if bed.vitality <= 0:
            bed.vitality = 0

        self.db.query(CareLog).filter(
            CareLog.garden_bed_id == bed.id,
            CareLog.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
        ).delete()
        self.db.commit()

        log_action(self.db, self.player_id, bed.id, ACTION_SPARK,
        "Вспышка Искры Роста",
        f"🌱+{balance.SPARK_GROWTH_PERCENT}% стадии ❤️-{balance.SPARK_VITALITY_COST}%",
        "neutral" if bed.vitality > 50 else "negative")

        self.db.commit()
        self.db.refresh(bed)
        return bed

    def harvest_bed(self, bed_id: int) -> dict:
        bed = self._get_living_bed(bed_id)

        plant = bed.plant
        result = {
            "plant_name": plant.name,
            "stage": bed.stage_name,
            "main_harvest": [],
            "bonus_harvest": [],
            "rare_harvest": [],
        }

        main_multiplier = formulas.get_harvest_multiplier(bed.growth_stage)

        quality = formulas.get_quality(bed.vitality)

        if plant.harvest_item_id:
            item = self.db.query(Item).filter(Item.id == plant.harvest_item_id).first()
        else:
            item = None

        if not item:
            item = Item(name=f"Ингредиент: {plant.name}", item_type="ingredient", rarity="common")
            self.db.add(item)
            self.db.flush()

        add_item_to_inventory(self.db, self.player_id, item.id, main_multiplier, quality, bed.id)
        
        result["main_harvest"].append({
            "name": item.name,
            "quantity": main_multiplier,
            "quality": quality
        })

        total_bonus = formulas.roll_bonus_drops(bed.essence)

        if total_bonus > 0:
            bonus_items = self.db.query(Item).filter(Item.item_type == "bonus").all()
            if bonus_items:
                for _ in range(total_bonus):
                    bonus_item = random.choices(
                        bonus_items,
                        weights=[100 if i.rarity == "common" else 40 if i.rarity == "uncommon" else 10 for i in bonus_items],
                        k=1
                    )[0]
                    add_item_to_inventory(self.db, self.player_id, bonus_item.id, 1, "Обычный", bed.id)
                    result["bonus_harvest"].append({"name": bonus_item.name, "rarity": bonus_item.rarity})

        rare_luck = has_perk(self.db, plant.id, PERK_RARE_LUCK_10)
        if formulas.roll_rare_drop(bed.essence, bed.growth_stage, rare_luck_perk=rare_luck):
            rare_items = self.db.query(Item).filter(Item.item_type == "rare").all()
            if rare_items:
                rare_item = random.choice(rare_items)
                add_item_to_inventory(self.db, self.player_id, rare_item.id, 1, "Редкий", bed.id)
                result["rare_harvest"].append({"name": rare_item.name, "rarity": rare_item.rarity})

        bed.essence = 0
        bed.vitality = max(bed.vitality - balance.HARVEST_VITALITY_COST, 0)
        bed.growth_stage = max(
            bed.growth_stage - balance.HARVEST_STAGE_ROLLBACK,
            bed.plant.min_harvest_stage - balance.HARVEST_STAGE_ROLLBACK,
        )
        bed.last_harvested_at = datetime.utcnow()
        bed.recovery_until = datetime.utcnow() + timedelta(hours=balance.RECOVERY_HOURS)

        if bed.vitality <= 0:
            bed.vitality = 0  # смерть

        loot_parts = []
        for h in result["main_harvest"]:
            loot_parts.append(f"{h['quantity']}x {h['name']} ({h['quality']})")
        for b in result["bonus_harvest"]:
            loot_parts.append(f"{b['name']}")
        for r in result["rare_harvest"]:
            loot_parts.append(f"🌟 {r['name']}")

        details = " | ".join(loot_parts) if loot_parts else None

        log_action(self.db, self.player_id, bed.id, ACTION_HARVEST,
            "Сбор урожая",
            f"❤️-{balance.HARVEST_VITALITY_COST}% 🌱-{balance.HARVEST_STAGE_ROLLBACK}%",
            "positive",
            details)

        self.db.commit()
        return result

    def process_daily_update(self, bed: GardenBed) -> GardenBed:
        now = datetime.utcnow()

        if bed.last_daily_update:
            hours_since = (now - bed.last_daily_update).total_seconds() / 3600
            if hours_since < balance.HOURS_BETWEEN_UPDATES:
                return bed

        if bed.plant_id is None:
            bed.last_daily_update = now
            return bed

        if bed.is_dead:
            bed.last_daily_update = now
            return bed

        was_watered = (
            bed.last_watered_at is not None
            and bed.last_watered_at.date() >= (now - timedelta(hours=24)).date()
        )
        essence_decay = formulas.calculate_night_essence_decay(bed.essence, was_watered)
        bed.essence = max(bed.essence - essence_decay, 0)

        if not bed.is_in_zenith:
            bed.vitality = max(bed.vitality - balance.NIGHT_VITALITY_COST, 0)

        if formulas.can_level_up(bed.growth_stage):
            bed.growth_stage = min(bed.growth_stage + balance.DAILY_GROWTH_PERCENT, 100)

        bed.last_watered_at = None
        bed.last_cleaned_at = None
        bed.last_moon_bath_at = None
        bed.last_daily_update = now

        if bed.vitality <= 0:
            bed.vitality = 0

        self.db.query(CareLog).filter(
            CareLog.garden_bed_id == bed.id,
            CareLog.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
        ).delete()
        self.db.commit()

        log_action(self.db, self.player_id, bed.id, ACTION_DAILY,
        "Пробуждение",
        f"🌱+{balance.DAILY_GROWTH_PERCENT}% стадии ❤️-{balance.NIGHT_VITALITY_COST}%",
        "neutral")

        self.db.commit()
        return bed

    def process_all_daily_updates(self) -> list[GardenBed]:
        beds = self.get_player_garden()
        updated = []
        for bed in beds:
            if bed.plant_id is not None:
                bed = self.process_daily_update(bed)
                updated.append(bed)
        return updated
