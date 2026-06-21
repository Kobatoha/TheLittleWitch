from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.garden_bed import GardenBed
from app.models.plant import Plant
from app.models.player import Player


MAX_BEDS_PER_PLAYER = 4       # максимум грядок у одного игрока
PLANT_COST_ENERGY = 10        # энергия на посадку

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
