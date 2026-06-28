"""
ГРИМУАР БАЛАНСА
Все цифры, которые влияют на геймплей — здесь.
Меняй смело, перезапускать сервер не нужно (если не кэшируются).
"""

# ===================== САД =====================

# Грядки
MAX_BEDS_PER_PLAYER = 4

# Полив (ежедневный уход)
WATER_VITALITY_BOOST = 15        # +% живучести за полив
WATER_ESSENCE_BOOST = 10         # базовая +эссенция (перебивается растением)

# Искра Роста (предмет)
SPARK_GROWTH_PERCENT = 4         # +% стадии за Искру
SPARK_VITALITY_COST = 5          # -% живучести за Искру
SPARK_ESSENCE_BOOST = 0          # искра не даёт эссенцию

# Ежедневный цикл (ночь)
DAILY_GROWTH_PERCENT = 4         # +% стадии за ночь
NIGHT_VITALITY_COST = 5          # -% живучести за ночь
NIGHT_ESSENCE_DECAY_PERCENT = 20 # -% эссенции за ночь без полива (0 если поливал)
HOURS_BETWEEN_UPDATES = 24       # часы между обновлениями

# Сбор урожая
HARVEST_VITALITY_COST = 20       # -% живучести при сборе
HARVEST_STAGE_ROLLBACK = 10      # откат стадии при сборе
RECOVERY_HOURS = 24              # часы восстановления после сбора

# Зрелость и Зенит
ZENITH_GRACE_HOURS = 24          # сколько часов растение держится на пике (100%)
WITHER_START_STAGE = 100         # стадия, после которой начинается увядание

# Лунная ванна
MOON_BATH_VITALITY_BOOST = 10     # +% живучести
MOON_BATH_ESSENCE_BOOST = 15      # +эссенции
MOON_BATH_COOLDOWN_DAYS = 3       # раз в 3 дня

ESSENCE_BAR_MAX = 200            # максимум эссенции для отображения бара (100% ширины)

# Луна
LUNAR_CYCLE_DAYS = 29.53

# ===================== КАЧЕСТВО УРОЖАЯ =====================

QUALITY_WITHERED = "Увядший"
QUALITY_NORMAL = "Обычный"
QUALITY_JUICY = "Сочный"
QUALITY_SPARKLING = "Искрящийся"

# Пороги живучести для качества
QUALITY_THRESHOLD_SPARKLING = 100  # 100%+ → Искрящийся
QUALITY_THRESHOLD_JUICY = 80       # 80-99% → Сочный
QUALITY_THRESHOLD_NORMAL = 50      # 50-79% → Обычный
# < 50% → Увядший


# ===================== СТАДИИ РОСТА =====================

STAGES = [
    (0, "Семя"),
    (20, "Росток"),
    (40, "Стебель"),
    (60, "Бутон"),
    (80, "Цветение"),
    (100, "Зрелость"),
]

MIN_HARVEST_STAGE = 60  # Бутон — минимальная стадия для сбора

# Множители урожая по стадиям
HARVEST_MULTIPLIER_BUD = 1        # Бутон (60-79%)
HARVEST_MULTIPLIER_BLOOM = 2      # Цветение (80-94%)
HARVEST_MULTIPLIER_ZENITH = 3     # Зрелость (95-100%)


# ===================== РЕДКАЯ УДАЧА =====================

RARE_DROP_BASE_CHANCE = 0.01      # 1% базовый шанс
RARE_DROP_ESSENCE_BONUS = 0.01    # +1% при 100+ эссенции
RARE_DROP_ZENITH_BONUS = 0.01     # +1% на стадии Зрелость (95%+)


# ===================== БОНУСНЫЙ ДРОП =====================

BONUS_DROP_ESSENCE_DIVIDER = 25   # эссенция / X = базовое количество бонусов
BONUS_RARITY_WEIGHTS = {
    "common": 100,
    "uncommon": 40,
    "rare": 10,
    "epic": 2,
}