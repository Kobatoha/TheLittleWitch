from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.garden_bed import GardenBed
from app.models.plant import Plant
from app.models.player import Player


MAX_BEDS_PER_PLAYER = 4       # максимум грядок у одного игрока
PLANT_COST_ENERGY = 10        # энергия на посадку
WATER_COST_ENERGY = 5           # энергия на полив
WATER_MOISTURE_BOOST = 30       # сколько влажности добавляет полив
MAX_MOISTURE = 100              # максимум влажности

def get_player_garden(db: Session, player_id: int):
    """Возвращает все грядки игрока."""
    return db.query(GardenBed).filter(GardenBed.player_id == player_id).all()

def can_plant(db: Session, player_id: int) -> tuple[bool, str]:
    """Проверяет, можно ли сажать (не превышен лимит грядок, есть ли энергия)."""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        return False, "Игрок не найден"

    beds_count = db.query(GardenBed).filter(
        GardenBed.player_id == player_id,
        GardenBed.plant_id != None  # считаем только занятые
    ).count()

    if beds_count >= MAX_BEDS_PER_PLAYER:
        return False, f"Максимум {MAX_BEDS_PER_PLAYER} грядок. Освободи одну!"

    if player.energy < PLANT_COST_ENERGY:
        return False, f"Недостаточно энергии! Нужно {PLANT_COST_ENERGY}, у тебя {player.energy}"

    return True, ""

def plant_seed(db: Session, player_id: int, plant_id: int) -> GardenBed:
    """Сажает растение на свободную грядку."""
    # Проверка
    ok, error = can_plant(db, player_id)
    if not ok:
        raise ValueError(error)

    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise ValueError("Растение не найдено")

    # Ищем пустую грядку
    bed = db.query(GardenBed).filter(
        GardenBed.player_id == player_id,
        GardenBed.plant_id == None
    ).first()

    if not bed:
        # Создаём новую грядку, если есть слот
        bed = GardenBed(player_id=player_id)

    now = datetime.utcnow()
    bed.plant_id = plant_id
    bed.planted_at = now
    bed.ready_at = now + timedelta(minutes=plant.growth_time)
    bed.moisture = 50
    bed.times_watered = 0

    # Тратим энергию
    player = db.query(Player).filter(Player.id == player_id).first()
    player.energy -= PLANT_COST_ENERGY

    db.add(bed)
    db.commit()
    db.refresh(bed)
    return bed

def can_water(db: Session, player_id: int, bed_id: int) -> tuple[bool, str]:
    """Проверяет, можно ли полить грядку."""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        return False, "Игрок не найден"

    if player.energy < WATER_COST_ENERGY:
        return False, f"Недостаточно энергии! Нужно {WATER_COST_ENERGY}, у тебя {player.energy}"

    bed = db.query(GardenBed).filter(
        GardenBed.id == bed_id,
        GardenBed.player_id == player_id
    ).first()
    if not bed:
        return False, "Грядка не найдена"
    if bed.plant_id is None:
        return False, "На грядке ничего не растёт"
    if bed.ready_at and bed.ready_at <= datetime.utcnow():
        return False, "Растение уже созрело, поливать не нужно!"
    if bed.moisture >= MAX_MOISTURE:
        return False, "Влажность уже максимальная"

    return True, ""

def water_bed(db: Session, player_id: int, bed_id: int) -> GardenBed:
    """Поливает грядку: тратит энергию, добавляет влажность, ускоряет рост."""
    ok, error = can_water(db, player_id, bed_id)
    if not ok:
        raise ValueError(error)

    bed = db.query(GardenBed).filter(
        GardenBed.id == bed_id,
        GardenBed.player_id == player_id
    ).first()

    # Тратим энергию игрока
    player = db.query(Player).filter(Player.id == player_id).first()
    player.energy -= WATER_COST_ENERGY

    # Увеличиваем влажность
    bed.moisture = min(bed.moisture + WATER_MOISTURE_BOOST, MAX_MOISTURE)
    bed.times_watered += 1

    # Ускоряем рост: вычитаем water_bonus минут из ready_at
    if bed.plant and bed.ready_at:
        bonus_minutes = bed.plant.water_bonus  # например, 15 минут
        bed.ready_at = bed.ready_at - timedelta(minutes=bonus_minutes)

    db.commit()
    db.refresh(bed)
    return bed

# === НОВЫЙ ПОЛИВ (система Живучесть/Эссенция/Цикл) ===

def water_bed_new(db: Session, player_id: int, bed_id: int) -> GardenBed:
    """Полив по новой системе: +Эссенция, +Цикл Роста, +Живучесть."""
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
        raise ValueError("Растение уже достигло Зрелости! Собирай урожай.")

    plant = bed.plant

    # Тратим энергию
    player.energy -= WATER_COST_ENERGY

    # Повышаем Живучесть (но не выше базовой)
    bed.vitality = min(bed.vitality + 15, plant.base_vitality)

    # Повышаем Эссенцию
    bed.essence += plant.essence_per_care

    # Продвигаем Цикл Роста
    bed.growth_stage = min(bed.growth_stage + plant.growth_per_care, 100)

    # Старую систему тоже обновляем (для совместимости)
    bed.moisture = min(bed.moisture + 30, 100)
    bed.times_watered += 1
    if bed.ready_at:
        bed.ready_at = bed.ready_at - __import__("datetime").timedelta(minutes=plant.water_bonus)

    db.commit()
    db.refresh(bed)
    return bed
