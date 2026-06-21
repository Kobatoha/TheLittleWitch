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
        raise ValueError("Растение погибло.")
    if not bed.can_water:
        if bed.recovery_until and bed.recovery_until > datetime.utcnow():
            raise ValueError(f"Растение восстанавливается до {format_dt(bed.recovery_until)}")
        raise ValueError("Полив уже использован сегодня. Используй Искру Роста!")

    plant = bed.plant

    # Восстановление живучести
    bed.vitality = min(bed.vitality + 15, plant.base_vitality)
    bed.essence += plant.essence_per_care
    bed.last_watered_at = datetime.utcnow()

    db.commit()
    db.refresh(bed)
    return bed
    
# === СБОР УРОЖАЯ ===

def harvest_bed(db: Session, player_id: int, bed_id: int) -> dict:
    bed = db.query(GardenBed).filter(
        GardenBed.id == bed_id,
        GardenBed.player_id == player_id
    ).first()
    if not bed:
        raise ValueError("Грядка не найдена")
    if bed.plant_id is None:
        raise ValueError("На грядке ничего не растёт")
    if bed.is_dead:
        raise ValueError("Растение погибло.")
    if not bed.can_harvest:
        raise ValueError(f"Нельзя собрать! Восстановление до {format_dt(bed.recovery_until)}" if bed.recovery_until else "Ещё рано собирать!")

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

    # === БРОСОК 2: Качество ===
    if bed.vitality >= 100:
        quality = "Искрящийся"
    elif bed.vitality >= 80:
        quality = "Сочный"
    elif bed.vitality >= 50:
        quality = "Обычный"
    else:
        quality = "Увядший"

    # Находим/создаём предмет
    item = db.query(Item).filter(Item.name.ilike(f"%{plant.name.split()[0]}%")).first()
    if not item:
        item = Item(name=f"Ингредиент: {plant.name}", item_type="ingredient", rarity="common")
        db.add(item)
        db.flush()

    inv_entry = Inventory(
        player_id=player_id,
        item_id=item.id,
        quantity=main_multiplier,
        quality=quality,
        source_bed_id=bed.id
    )
    db.add(inv_entry)
    result["main_harvest"].append({
        "name": item.name,
        "quantity": main_multiplier,
        "quality": quality
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
                    weights=[100 if i.rarity == "common" else 40 if i.rarity == "uncommon" else 10 for i in bonus_items],
                    k=1
                )[0]
                inv_bonus = Inventory(
                    player_id=player_id,
                    item_id=bonus_item.id,
                    quantity=1,
                    source_bed_id=bed.id
                )
                db.add(inv_bonus)
                result["bonus_harvest"].append({"name": bonus_item.name, "rarity": bonus_item.rarity})

    # === БРОСОК 4: Редкая удача ===
    rare_chance = 1.0
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

    # === ПОСЛЕ СБОРА: растение остаётся, но страдает ===
    bed.essence = 0
    bed.vitality = max(bed.vitality - 20, 0)  # -20 Живучести, но не ниже 0
    bed.growth_stage = max(bed.growth_stage - 10, bed.plant.min_harvest_stage - 10)  # откат на 10%
    bed.last_harvested_at = datetime.utcnow()
    bed.recovery_until = datetime.utcnow() + timedelta(days=1)  # 1 день восстановления (потом можно на 5)

    if bed.vitality <= 0:
        bed.vitality = 0  # смерть

    db.commit()
    return result

def use_growth_spark(db: Session, player_id: int, bed_id: int) -> GardenBed:
    bed = db.query(GardenBed).filter(
        GardenBed.id == bed_id,
        GardenBed.player_id == player_id
    ).first()
    if not bed:
        raise ValueError("Грядка не найдена")
    if bed.plant_id is None:
        raise ValueError("На грядке ничего не растёт")
    if bed.is_dead:
        raise ValueError("Растение погибло")
    if bed.growth_stage >= 100:
        raise ValueError("Растение уже в Зрелости!")

    spark_item = db.query(Item).filter(Item.name == "Искра Роста").first()
    if not spark_item:
        raise ValueError("Предмет 'Искра Роста' не найден в БД")

    inv = db.query(Inventory).filter(
        Inventory.player_id == player_id,
        Inventory.item_id == spark_item.id,
        Inventory.quantity > 0
    ).first()
    if not inv:
        raise ValueError("У тебя нет Искры Роста!")

    # Тратим Искру
    inv.quantity -= 1
    if inv.quantity <= 0:
        db.delete(inv)

    # Сбрасываем дневной лимит полива
    bed.last_watered_at = None
    bed.recovery_until = None

    # Рост: +4% к стадии
    bed.growth_stage = min(bed.growth_stage + 4, 100)

    # Живучесть падает на 5% (ночной стресс)
    bed.vitality = max(bed.vitality - 5, 0)

    # Эссенция: если вчера поливали — не падает, иначе -20%
    yesterday = datetime.utcnow().date() - timedelta(days=1)
    if bed.last_watered_at and bed.last_watered_at.date() >= yesterday:
        pass  # эссенция не падает
    else:
        bed.essence = max(bed.essence - int(bed.essence * 0.2), 0)

    if bed.vitality <= 0:
        bed.vitality = 0

    db.commit()
    db.refresh(bed)
    return bed
