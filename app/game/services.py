import random
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.garden_bed import GardenBed
from app.models.inventory import Inventory
from app.models.item import Item
from app.models.plant import Plant
from app.models.player import Player


MAX_BEDS_PER_PLAYER = 4

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

    db.add(bed)
    db.commit()
    db.refresh(bed)
    return bed


# === ПОЛИВ ===

def water_bed(db: Session, player_id: int, bed_id: int) -> GardenBed:
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise ValueError("Игрок не найден")

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

    bed.vitality = min(bed.vitality + 15, plant.base_vitality)
    bed.essence += plant.essence_per_care
    bed.growth_stage = min(bed.growth_stage + plant.growth_per_care, 100)

    db.commit()
    db.refresh(bed)
    return bed
    
# === СБОР УРОЖАЯ ===

def harvest_bed(db: Session, player_id: int, bed_id: int) -> dict:
    """Собирает урожай с грядки. Возвращает словарь с результатами."""
    bed = db.query(GardenBed).filter(
        GardenBed.id == bed_id,
        GardenBed.player_id == player_id
    ).first()
    if not bed:
        raise ValueError("Грядка не найдена")
    if bed.plant_id is None:
        raise ValueError("На грядке ничего не растёт")
    if bed.is_dead:
        raise ValueError("Растение погибло. Урожая нет.")
    if not bed.can_harvest:
        raise ValueError(f"Ещё рано собирать! Нужна стадия Бутон (60%%), сейчас: {bed.stage_name} ({bed.growth_stage}%%)")

    plant = bed.plant
    result = {
        "plant_name": plant.name,
        "stage": bed.stage_name,
        "main_harvest": [],
        "bonus_harvest": [],
        "rare_harvest": [],
    }

    # === БРОСОК 1: Основной урожай ===
    if bed.growth_stage >= 95:
        main_multiplier = 3
    elif bed.growth_stage >= 80:
        main_multiplier = 2
    else:
        main_multiplier = 1

    main_count = main_multiplier  # базовое количество = 1 × множитель

    # === БРОСОК 2: Качество ===
    if bed.vitality >= 100:
        quality = "Искрящийся"
        quality_mult = 2.0
    elif bed.vitality >= 80:
        quality = "Сочный"
        quality_mult = 1.5
    elif bed.vitality >= 50:
        quality = "Обычный"
        quality_mult = 1.0
    else:
        quality = "Увядший"
        quality_mult = 0.5

    # Находим предмет ингредиента
    ingredient_name = f"{'Корень' if 'Мандрагора' in plant.name else 'Лепесток' if 'Лилия' in plant.name else plant.name}"
    item = db.query(Item).filter(Item.name.contains(plant.name.split()[0])).first()
    if not item:
        # Если предмет не найден — создаём временную запись (на будущее)
        item = Item(name=f"Ингредиент: {plant.name}", item_type="ingredient", rarity="common")
        db.add(item)
        db.flush()

    # Добавляем в инвентарь
    inv_entry = Inventory(
        player_id=player_id,
        item_id=item.id,
        quantity=main_count,
        quality=quality,
        source_bed_id=bed.id
    )
    db.add(inv_entry)
    result["main_harvest"].append({
        "name": item.name,
        "quantity": main_count,
        "quality": quality,
        "quality_mult": quality_mult
    })

    # === БРОСОК 3: Бонусный дроп ===
    base_bonus = bed.essence // 25
    dice_bonus = random.randint(0, base_bonus)
    total_bonus = base_bonus + dice_bonus

    if total_bonus > 0:
        bonus_items = db.query(Item).filter(Item.item_type == "bonus").all()
        if bonus_items:
            for _ in range(total_bonus):
                bonus_item = random.choices(
                    bonus_items,
                    weights=[100 if i.rarity == "common" else 40 if i.rarity == "uncommon" else 10 if i.rarity == "rare" else 2 for i in bonus_items],
                    k=1
                )[0]
                inv_bonus = Inventory(
                    player_id=player_id,
                    item_id=bonus_item.id,
                    quantity=1,
                    quality="Обычный",
                    source_bed_id=bed.id
                )
                db.add(inv_bonus)
                result["bonus_harvest"].append({"name": bonus_item.name, "rarity": bonus_item.rarity})

    # === БРОСОК 4: Редкая удача ===
    rare_chance = 1.0  # базовый 1%
    if bed.essence >= 100:
        rare_chance += 1.0
    if bed.growth_stage >= 95:
        rare_chance += 1.0

    if random.random() * 100 < rare_chance:
        rare_items = db.query(Item).filter(Item.item_type == "rare").all()
        if rare_items:
            rare_item = random.choice(rare_items)
            inv_rare = Inventory(
                player_id=player_id,
                item_id=rare_item.id,
                quantity=1,
                quality="Редкий",
                source_bed_id=bed.id
            )
            db.add(inv_rare)
            result["rare_harvest"].append({"name": rare_item.name, "rarity": rare_item.rarity})

    # Очищаем грядку после сбора
    bed.plant_id = None
    bed.vitality = 100
    bed.essence = 0
    bed.growth_stage = 0

    db.commit()
    return result
    