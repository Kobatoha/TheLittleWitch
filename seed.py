from app.core.database import SessionLocal
from app.models.plant import Plant

def seed_plants():
    db = SessionLocal()
    plants = [
        Plant(
            name="Мандрагора",
            description="Корень кричит при сборе. Очень живучая.",
            base_vitality=120,
            vitality_decay=3,
            essence_per_care=10,
            growth_per_care=7,
            min_harvest_stage=60,
            base_potency=100,
        ),
        Plant(
            name="Лунная лилия",
            description="Цветёт только под луной. Высокая эссенция.",
            base_vitality=80,
            vitality_decay=8,
            essence_per_care=18,
            growth_per_care=10,
            min_harvest_stage=70,
            base_potency=100,
            icon="plants/lunar_lily/lily.png",
        ),
        Plant(
            name="Шипучка болотная",
            description="Растёт быстро, но слабая магически.",
            base_vitality=100,
            vitality_decay=5,
            essence_per_care=6,
            growth_per_care=12,
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
    