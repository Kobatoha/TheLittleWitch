from app.core.database import SessionLocal
from app.models.plant import Plant

def seed_plants():
    db = SessionLocal()
    plants = [
        Plant(name="Мандрагора", growth_time=60, water_bonus=15, base_harvest_count=1, description="Корень кричит при сборе"),
        Plant(name="Лунная лилия", growth_time=120, water_bonus=20, base_harvest_count=2, description="Цветёт только ночью"),
        Plant(name="Шипучка болотная", growth_time=30, water_bonus=10, base_harvest_count=3, description="Быстро растёт, дёшево стоит"),
    ]
    for p in plants:
        existing = db.query(Plant).filter(Plant.name == p.name).first()
        if not existing:
            db.add(p)
    db.commit()
    db.close()
    print("Растения посеяны в БД!")

if __name__ == "__main__":
    seed_plants()
