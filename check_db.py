import sqlite3
from app.core.config import DATABASE_URL

# Убираем префикс sqlite:///
db_path = DATABASE_URL.replace("sqlite:///", "")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Проверяем alembic_version
try:
    cursor.execute("SELECT * FROM alembic_version")
    row = cursor.fetchone()
    print(f"Текущая версия в БД: {row[0] if row else 'пусто'}")
except Exception as e:
    print(f"Ошибка чтения alembic_version: {e}")

conn.close()
