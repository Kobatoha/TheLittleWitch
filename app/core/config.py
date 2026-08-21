import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATABASE_PATH = BASE_DIR / "app.db"

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:sirok123@localhost:5432/tlw"
)

# Временный ID игрока (потом заменим на авторизацию)
TEMP_PLAYER_ID: int = 1

