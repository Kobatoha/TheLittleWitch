from app.core.database import SessionLocal
from app.models.plant import Plant
from app.models.item import Item

def seed_plants():
    db = SessionLocal()

    mandrake_item = db.query(Item).filter(Item.name == "Корень мандрагоры").first()
    lily_item = db.query(Item).filter(Item.name == "Лепесток лунной лилии").first()
    bog_item = db.query(Item).filter(Item.name == "Шипучка болотная").first()

    plants = [
        # Лунная лилия
        Plant(
            name="Лунная лилия",
            description="Цветёт только под луной. Высокая эссенция.",
            base_vitality=80,
            vitality_decay=8,
            essence_per_care=18,
            growth_per_care=10,
            min_harvest_stage=70,
            base_potency=100,
            icon_seed="plants/lunar_lily/seed.png",
            icon_sprout="plants/lunar_lily/sprout.png",
            icon_stem="plants/lunar_lily/stem.png",
            icon_bud="plants/lunar_lily/bud.png",
            icon_bloom="plants/lunar_lily/bloom.png",
            icon_mature="plants/lunar_lily/mature.png",
            harvest_item_id=lily_item.id if lily_item else None,
        ),
        # Мандрагора
        Plant(
            name="Мандрагора",
            description="Корень кричит при сборе. Очень живучая.",
            base_vitality=120,
            vitality_decay=3,
            essence_per_care=10,
            growth_per_care=7,
            min_harvest_stage=60,
            base_potency=100,
            icon_seed="plants/mandrake/seed.png",
            icon_sprout="plants/mandrake/sprout.png",
            icon_stem="plants/mandrake/stem.png",
            icon_bud="plants/mandrake/bud.png",
            icon_bloom="plants/mandrake/bloom.png",
            icon_mature="plants/mandrake/mature.png",
            harvest_item_id=mandrake_item.id if mandrake_item else None,
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
            harvest_item_id=bog_item.id if bog_item else None,
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
    