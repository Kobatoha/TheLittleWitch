"""
ФОРМУЛЫ РАСЧЁТА
Чистые функции без побочных эффектов.
Принимают числа → возвращают числа.
"""
import random
from app.core import balance


def get_stage_name(growth_stage: int) -> str:
    for threshold, name in reversed(balance.STAGES):
        if growth_stage >= threshold:
            return name
    return "Семя"


def get_harvest_multiplier(growth_stage: int) -> int:
    if growth_stage >= 95:
        return balance.HARVEST_MULTIPLIER_ZENITH
    elif growth_stage >= 80:
        return balance.HARVEST_MULTIPLIER_BLOOM
    else:
        return balance.HARVEST_MULTIPLIER_BUD


def get_quality(vitality: int) -> str:
    if vitality >= balance.QUALITY_THRESHOLD_SPARKLING:
        return balance.QUALITY_SPARKLING
    elif vitality >= balance.QUALITY_THRESHOLD_JUICY:
        return balance.QUALITY_JUICY
    elif vitality >= balance.QUALITY_THRESHOLD_NORMAL:
        return balance.QUALITY_NORMAL
    else:
        return balance.QUALITY_WITHERED


def get_quality_multiplier(quality: str) -> float:
    multipliers = {
        balance.QUALITY_SPARKLING: 2.0,
        balance.QUALITY_JUICY: 1.5,
        balance.QUALITY_NORMAL: 1.0,
        balance.QUALITY_WITHERED: 0.5,
    }
    return multipliers.get(quality, 1.0)


def roll_bonus_drops(essence: int) -> int:
    base = essence // balance.BONUS_DROP_ESSENCE_DIVIDER
    dice = random.randint(0, base)
    return base + dice


def roll_rare_drop(essence: int, growth_stage: int) -> bool:
    chance = balance.RARE_DROP_BASE_CHANCE
    if essence >= 100:
        chance += balance.RARE_DROP_ESSENCE_BONUS
    if growth_stage >= 95:
        chance += balance.RARE_DROP_ZENITH_BONUS
    return random.random() < chance


def calculate_night_essence_decay(essence: int, was_watered_yesterday: bool) -> int:
    if was_watered_yesterday:
        return 0
    return int(essence * balance.NIGHT_ESSENCE_DECAY_PERCENT / 100)


def can_level_up(growth_stage: int) -> bool:
    return growth_stage < balance.WITHER_START_STAGE
    