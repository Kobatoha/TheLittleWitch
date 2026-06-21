from app.core.database import SessionLocal
from app.models.plant import Plant

def seed_plants():
    db = SessionLocal()
    plants = [
        Plant(
            name="Мандрагора",
            description="Корень кричит при сборе. Очень живучая.",
            growth_time=60,           # старая система
            water_bonus=15,
            base_harvest_count=1,
            base_vitality=120,        # новая: живучее других
            vitality_decay=3,         # новая: медленно увядает
            essence_per_care=10,
            growth_per_care=7,
            min_harvest_stage=60,
            base_potency=100,
        ),
        Plant(
            name="Лунная лилия",
            description="Цветёт только под луной. Высокая эссенция.",
            growth_time=120,
            water_bonus=20,
            base_harvest_count=2,
            base_vitality=80,         # новая: нежная
            vitality_decay=8,         # новая: быстро увядает без ухода
            essence_per_care=18,      # новая: много эссенции
            growth_per_care=10,
            min_harvest_stage=70,
            base_potency=100,
        ),
        Plant(
            name="Шипучка болотная",
            description="Растёт быстро, но слабая магически.",
            growth_time=30,
            water_bonus=10,
            base_harvest_count=3,
            base_vitality=100,
            vitality_decay=5,
            essence_per_care=6,       # новая: мало эссенции
            growth_per_care=12,       # новая: быстро растёт
            min_harvest_stage=50,
            base_potency=100,
        ),
    ]

    for p in plants:
        existing = db.query(Plant).filter(Plant.name == p.name).first()
        if not existing:
            db.add(p)
            print(f"  🌱 {p.name} добавлен")
        else:
            # Обновим существующие растения новыми полями
            for key, value in p.__dict__.items():
                if not key.startswith("_") and key != "id":
                    setattr(existing, key, value)
            print(f"  🔄 {p.name} обновлён")

    db.commit()
    db.close()
    print("✅ Растения в БД!")

if __name__ == "__main__":
    seed_plants()
    