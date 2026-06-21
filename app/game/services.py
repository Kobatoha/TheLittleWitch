from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.garden_bed import GardenBed
from app.models.plant import Plant
from app.models.player import Player


MAX_BEDS_PER_PLAYER = 4
PLANT_COST_ENERGY = 10
WATER_COST_ENERGY = 5

# === САД ===

def get_player_garden(db: Session, player_id: int):
    return db.query(GardenBed).filter(GardenBed.player_id == player_id).all()


# === ПОСАДКА ===

def plant_seed(db: Session, player_id: int, plant_id: int) -> GardenBed:
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise ValueError("Игрок не найден")

    beds_count = db.query(GardenBed).filter(
        GardenBed.player_id == player_id,
        GardenBed.plant_id != None
    ).count()
    if beds_count >= MAX_BEDS_PER_PLAYER:
        raise ValueError(f"Максимум {MAX_BEDS_PER_PLAYER} грядок. Освободи одну!")

    if player.energy < PLANT_COST_ENERGY:
        raise ValueError(f"Недостаточно энергии! Нужно {PLANT_COST_ENERGY}, у тебя {player.energy}")

    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise ValueError("Растение не найдено")

    # Ищем пустую грядку или создаём новую
    bed = db.query(GardenBed).filter(
        GardenBed.player_id == player_id,
        GardenBed.plant_id == None
    ).first()
    if not bed:
        bed = GardenBed(player_id=player_id)

    bed.plant_id = plant_id
    bed.vitality = plant.base_vitality
    bed.essence = 0
    bed.growth_stage = 0
    bed.planted_at = datetime.utcnow()

    player.energy -= PLANT_COST_ENERGY

    db.add(bed)
    db.commit()
    db.refresh(bed)
    return bed


# === ПОЛИВ ===

def water_bed(db: Session, player_id: int, bed_id: int) -> GardenBed:
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise ValueError("Игрок не найден")
    if player.energy < WATER_COST_ENERGY:
        raise ValueError(f"Недостаточно энергии! Нужно {WATER_COST_ENERGY}, у тебя {player.energy}")

    bed = db.query(GardenBed).filter(
        GardenBed.id == bed_id,
        GardenBed.player_id == player_id
    ).first()
    if not bed:
        raise ValueError("Грядка не найдена")
    if bed.plant_id is None:
        raise ValueError("На грядке ничего не растёт")
    if bed.is_dead:
        raise ValueError("Растение погибло. Удали его и посади новое.")
    if bed.growth_stage >= 100:
        raise ValueError("Растение уже в Зрелости! Собирай урожай.")

    plant = bed.plant

    player.energy -= WATER_COST_ENERGY
    bed.vitality = min(bed.vitality + 15, plant.base_vitality)
    bed.essence += plant.essence_per_care
    bed.growth_stage = min(bed.growth_stage + plant.growth_per_care, 100)

    db.commit()
    db.refresh(bed)
    return bed
    