import random
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core import config
from app.core import balance

from app.game import formulas
from app.game.utils import format_dt
from app.game.moon import get_essence_bonus_for_night, get_moon_phase

from app.models.garden_bed import GardenBed
from app.models.inventory import Inventory
from app.models.item import Item
from app.models.plant import Plant
from app.models.player import Player
from app.models.care_log import CareLog


def log_action(db: Session, player_id: int, bed_id: int, action: str, action_name: str, effect: str, mood: str = "neutral", details: str = None):
    """Записывает действие в лог ухода."""
    log = CareLog(
        garden_bed_id=bed_id,
        player_id=player_id,
        action=action,
        action_name=action_name,
        effect=effect,
        mood=mood,
        details=details
    )
    db.add(log)
    db.commit()


def add_item_to_inventory(db: Session, player_id: int, item_id: int, quantity: int = 1, quality: str = "Обычный", source_bed_id: int = None) -> Inventory:
    """Добавляет предмет в инвентарь. Если такой же уже есть — увеличивает количество."""
    existing = db.query(Inventory).filter(
        Inventory.player_id == player_id,
        Inventory.item_id == item_id,
        Inventory.quality == quality
    ).first()

    if existing:
        existing.quantity += quantity
        db.commit()
        return existing
    else:
        inv = Inventory(
            player_id=player_id,
            item_id=item_id,
            quantity=quantity,
            quality=quality,
            source_bed_id=source_bed_id
        )
        db.add(inv)
        db.commit()
        db.refresh(inv)
        return inv

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
    if beds_count >= balance.MAX_BEDS_PER_PLAYER:
        raise ValueError(f"Максимум {balance.MAX_BEDS_PER_PLAYER} грядок. Освободи одну!")

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
    bed.vitality = min(bed.vitality + balance.WATER_VITALITY_BOOST, max(plant.base_vitality, 100))
    bed.essence += plant.essence_per_care  # растение диктует прирост эссенции
    bed.growth_stage = min(bed.growth_stage, 100)  # не двигаем, только если не формула
    bed.last_watered_at = datetime.utcnow()

    log_action(db, player_id, bed.id, "water",
    "Орошение лунной росой",
    f"❤️+{balance.WATER_VITALITY_BOOST}% ✨+{plant.essence_per_care}",
    "positive")

    db.commit()
    db.refresh(bed)
    return bed

# === ПРОПОЛКА ===

def clean_bed(db: Session, player_id: int, bed_id: int) -> GardenBed:
    """Прополка: +2 Эссенции, +5 Живучести. Лимит — раз в сутки."""
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
    if bed.recovery_until and bed.recovery_until > datetime.utcnow():
        raise ValueError(f"Растение восстанавливается до {bed.recovery_until.strftime('%d.%m.%Y %H:%M')}")

    # Проверка дневного лимита прополки
    if bed.last_cleaned_at and bed.last_cleaned_at.date() >= datetime.utcnow().date():
        raise ValueError("Прополка уже использована сегодня.")

    plant = bed.plant

    bed.vitality = min(bed.vitality + balance.WATER_VITALITY_BOOST, max(plant.base_vitality, 100))
    bed.essence += 2
    bed.last_cleaned_at = datetime.utcnow()

    # Случайная находка (20% шанс)
    details = None
    if random.random() < 0.2:
        findings = ["радужный пучеглаз", "сонная божья коровка", "крошка лунного камня", "пёрышко звёздной птицы"]
        details = f"Найден(а) {random.choice(findings)}!"

    log_action(db, player_id, bed.id, "clean",
        "Очищение листьев",
        f"❤️+5% ✨+2",
        "positive", details)

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
    main_multiplier = formulas.get_harvest_multiplier(bed.growth_stage)

    # === БРОСОК 2: Качество ===
    quality = formulas.get_quality(bed.vitality)

    # Находим/создаём предмет
    item = db.query(Item).filter(Item.name.ilike(f"%{plant.name.split()[0]}%")).first()
    if not item:
        item = Item(name=f"Ингредиент: {plant.name}", item_type="ingredient", rarity="common")
        db.add(item)
        db.flush()

    add_item_to_inventory(db, player_id, item.id, main_multiplier, quality, bed.id)
    
    result["main_harvest"].append({
        "name": item.name,
        "quantity": main_multiplier,
        "quality": quality
    })

    # === БРОСОК 3: Бонусный дроп ===
    total_bonus = formulas.roll_bonus_drops(bed.essence)

    if total_bonus > 0:
        bonus_items = db.query(Item).filter(Item.item_type == "bonus").all()
        if bonus_items:
            for _ in range(total_bonus):
                bonus_item = random.choices(
                    bonus_items,
                    weights=[100 if i.rarity == "common" else 40 if i.rarity == "uncommon" else 10 for i in bonus_items],
                    k=1
                )[0]
                add_item_to_inventory(db, player_id, bonus_item.id, 1, "Обычный", bed.id)
                result["bonus_harvest"].append({"name": bonus_item.name, "rarity": bonus_item.rarity})

    # === БРОСОК 4: Редкая удача ===
    if formulas.roll_rare_drop(bed.essence, bed.growth_stage):
        rare_items = db.query(Item).filter(Item.item_type == "rare").all()
        if rare_items:
            rare_item = random.choice(rare_items)
            add_item_to_inventory(db, player_id, rare_item.id, 1, "Редкий", bed.id)
            result["rare_harvest"].append({"name": rare_item.name, "rarity": rare_item.rarity})
        
    # === ПОСЛЕ СБОРА: растение остаётся, но страдает ===
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

    # === ЛОГ СО ВСЕМ ЛУТОМ ===
    loot_parts = []
    for h in result["main_harvest"]:
        loot_parts.append(f"{h['quantity']}x {h['name']} ({h['quality']})")
    for b in result["bonus_harvest"]:
        loot_parts.append(f"{b['name']}")
    for r in result["rare_harvest"]:
        loot_parts.append(f"🌟 {r['name']}")

    details = " | ".join(loot_parts) if loot_parts else None

    log_action(db, player_id, bed.id, "harvest",
        "Сбор урожая",
        f"❤️-{balance.HARVEST_VITALITY_COST}% 🌱-{balance.HARVEST_STAGE_ROLLBACK}%",
        "positive",
        details)

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
    bed.last_cleaned_at = None
    bed.recovery_until = None
    bed.last_moon_bath_at = None

    # Рост
    bed.growth_stage = min(bed.growth_stage + balance.SPARK_GROWTH_PERCENT, 100)
   
    # Живучесть
    bed.vitality = max(bed.vitality - balance.SPARK_VITALITY_COST, 0)

    # Эссенция — без изменений

    if bed.vitality <= 0:
        bed.vitality = 0
    
    # Очищаем логи за сегодня (новый день с искрой)
    db.query(CareLog).filter(
        CareLog.garden_bed_id == bed.id,
        CareLog.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
    ).delete()
    db.commit()

    log_action(db, player_id, bed.id, "spark",
    "Вспышка Искры Роста",
    f"🌱+{balance.SPARK_GROWTH_PERCENT}% стадии ❤️-{balance.SPARK_VITALITY_COST}%",
    "neutral" if bed.vitality > 50 else "negative")

    db.commit()
    db.refresh(bed)
    return bed

# === ЕЖЕДНЕВНОЕ ОБНОВЛЕНИЕ ===

def process_daily_update(db: Session, bed: GardenBed) -> GardenBed:
    """Обрабатывает ежедневное обновление для одного растения."""
    now = datetime.utcnow()

    # Проверяем, прошло ли достаточно времени с последнего обновления
    if bed.last_daily_update:
        hours_since = (now - bed.last_daily_update).total_seconds() / 3600
        if hours_since < balance.HOURS_BETWEEN_UPDATES:
            return bed  # ещё не время

    if bed.plant_id is None:
        bed.last_daily_update = now
        return bed

    if bed.is_dead:
        bed.last_daily_update = now
        return bed

    # === ЭССЕНЦИЯ ЗА НОЧЬ ===
    was_watered = (
        bed.last_watered_at is not None
        and bed.last_watered_at.date() >= (now - timedelta(hours=24)).date()
    )
    essence_decay = formulas.calculate_night_essence_decay(bed.essence, was_watered)
    bed.essence = max(bed.essence - essence_decay, 0)

    # === ЖИВУЧЕСТЬ (в Зените не падает) ===
    if not bed.is_in_zenith:
        bed.vitality = max(bed.vitality - balance.NIGHT_VITALITY_COST, 0)

    # === РОСТ (только если < 100%) ===
    if formulas.can_level_up(bed.growth_stage):
        bed.growth_stage = min(bed.growth_stage + balance.DAILY_GROWTH_PERCENT, 100)

    # === СБРОС ПОЛИВА (новый день) ===
    bed.last_watered_at = None
        
    # === СБРОС ПРОПОЛКИ (новый день) ===
    bed.last_cleaned_at = None

    # === ВОССТАНОВЛЕНИЕ ===
    if bed.recovery_until and bed.recovery_until <= now:
        bed.recovery_until = None

    bed.last_daily_update = now

    if bed.vitality <= 0:
        bed.vitality = 0  # смерть

    # Очищаем логи за сегодня (новый день с искрой)
    db.query(CareLog).filter(
        CareLog.garden_bed_id == bed.id,
        CareLog.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
    ).delete()
    db.commit()

    log_action(db, bed.player_id, bed.id, "daily",
    "Пробуждение",
    f"🌱+{balance.DAILY_GROWTH_PERCENT}% стадии ❤️-{balance.NIGHT_VITALITY_COST}%",
    "neutral")

    db.commit()
    return bed


def process_all_daily_updates(db: Session, player_id: int) -> list[GardenBed]:
    """Обновляет все растения игрока, если прошло достаточно времени."""
    beds = get_player_garden(db, player_id)
    updated = []
    for bed in beds:
        if bed.plant_id is not None:
            bed = process_daily_update(db, bed)
            updated.append(bed)
    return updated

# === МАГАЗИН ===

def sell_item(db: Session, player_id: int, inventory_id: int, sell_quantity: int = 1) -> dict:
    """Продаёт предмет из инвентаря. Возвращает результат."""
    inv = db.query(Inventory).filter(
        Inventory.id == inventory_id,
        Inventory.player_id == player_id,
        Inventory.quantity > 0
    ).first()
    if not inv:
        raise ValueError("Предмет не найден в инвентаре")
    if sell_quantity > inv.quantity:
        raise ValueError(f"Недостаточно предметов! У тебя {inv.quantity} шт.")

    item = inv.item
    total_price = item.sell_price * sell_quantity

    # Списываем предмет
    inv.quantity -= sell_quantity
    if inv.quantity <= 0:
        db.delete(inv)

    # Добавляем монеты игроку
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise ValueError("Игрок не найден")
    player.coins += total_price

    db.commit()

    return {
        "item_name": item.name,
        "quantity_sold": sell_quantity,
        "price_per_item": item.sell_price,
        "total_coins_earned": total_price,
        "coins_now": player.coins,
        "remaining_quantity": inv.quantity if inv.quantity > 0 else 0
    }


def get_player_items_for_shop(db: Session, player_id: int) -> list:
    """Возвращает все предметы игрока для отображения в магазине."""
    items = db.query(Inventory).filter(
        Inventory.player_id == player_id,
        Inventory.quantity > 0
    ).order_by(Inventory.item.has(Item.item_type == "rare").desc(),
               Inventory.item.has(Item.sell_price).desc()).all()
    return items

# === ЛУННАЯ ВАННА ===

def moon_bath(db: Session, player_id: int, bed_id: int) -> GardenBed:
    """Выставить растение под лунный свет. Бонус зависит от фазы луны. Раз в сутки."""
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
    if bed.recovery_until and bed.recovery_until > datetime.utcnow():
        raise ValueError(f"Растение восстанавливается до {bed.recovery_until.strftime('%d.%m.%Y %H:%M')}")

    # Дневной лимит
    if bed.last_moon_bath_at and bed.last_moon_bath_at.date() >= datetime.utcnow().date():
        raise ValueError("Лунная ванна уже была сегодня. Жди завтра!")

    plant = bed.plant
    moon = get_moon_phase()
    bonus = moon["essence_bonus"]

    if bonus == 0:
        raise ValueError(f"{moon['emoji']} Сегодня {moon['name']} — лунный свет слишком слаб. Приходи в полнолуние!")

    # Бонус живучести и эссенции зависит от фазы
    vitality_bonus = bonus // 2  # половина от бонуса эссенции
    bed.vitality = min(bed.vitality + vitality_bonus, max(plant.base_vitality, 100))
    bed.essence += bonus
    bed.last_moon_bath_at = datetime.utcnow()

    log_action(db, player_id, bed.id, "moon",
    f"Лунная ванна ({moon['name']})",
    f"❤️+{vitality_bonus}% ✨+{bonus}",
    "positive" if bonus >= 10 else "neutral")

    db.commit()
    db.refresh(bed)
    return bed
    