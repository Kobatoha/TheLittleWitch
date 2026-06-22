import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATABASE_PATH = BASE_DIR / "app.db"

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH.as_posix()}")

# Временный ID игрока (потом заменим на авторизацию)
TEMP_PLAYER_ID = 1

# Сад
MAX_BEDS_PER_PLAYER = 4
DAILY_GROWTH_PERCENT = 4        # +% стадии в день
NIGHT_VITALITY_LOSS = 5         # -% живучести за ночь
WATER_VITALITY_BOOST = 15       # +живучести от полива
WATER_ESSENCE_BOOST = 10        # +эссенции от полива (базовый, перебивается plant.essence_per_care)
SPARK_GROWTH_PERCENT = 4        # +% стадии от Искры
SPARK_VITALITY_LOSS = 5         # -% живучести от Искры
SPARK_ESSENCE_BOOST = 10        # +эссенции от Искры
HARVEST_VITALITY_COST = 20      # -живучести при сборе
HARVEST_STAGE_ROLLBACK = 10     # откат стадии при сборе
RECOVERY_HOURS = 24             # часы восстановления после сбора
ESSENCE_DECAY_PERCENT = 20      # % потери эссенции без полива

# Качество урожая
QUALITY_WITHERED = "Увядший"
QUALITY_NORMAL = "Обычный"
QUALITY_JUICY = "Сочный"
QUALITY_SPARKLING = "Искрящийся"

# Редкая удача
RARE_DROP_BASE_CHANCE = 1.0     # базовый шанс %
RARE_DROP_ESSENCE_BONUS = 1.0   # +% при эссенции 100+
RARE_DROP_ZENITH_BONUS = 1.0    # +% при стадии Зрелость
