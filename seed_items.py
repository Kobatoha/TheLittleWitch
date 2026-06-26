from app.core.database import SessionLocal
from app.models.item import Item

def seed_items():
    db = SessionLocal()
    items = [
        # Основные ингредиенты
        Item(name="Корень мандрагоры", item_type="ingredient", rarity="common",
             description="Кричит при сборе.", sell_price=15),
        Item(name="Лепесток лунной лилии", item_type="ingredient", rarity="common",
             description="Светится в темноте.", sell_price=20),
        Item(name="Шипучка болотная", item_type="ingredient", rarity="common",
             description="Пузырится в котле.", sell_price=10),

        # Бонусные предметы
        Item(name="Капля утренней росы", item_type="bonus", rarity="common",
             description="Чистая влага.", sell_price=5),
        Item(name="Волшебная пыльца", item_type="bonus", rarity="uncommon",
             description="Мерцает.", sell_price=15),
        Item(name="Крошечный светлячок", item_type="bonus", rarity="rare",
             description="Живой огонёк.", sell_price=40),
        Item(name="Слеза феи", item_type="bonus", rarity="epic",
             description="Редкая и ценная.", sell_price=100),

        # Редкая удача
        Item(name="Семечко с потенциалом", item_type="rare", rarity="rare",
             description="Сила Рода +10.", sell_price=80, potency_boost=10),
        Item(name="Мутировавший корешок", item_type="rare", rarity="epic",
             description="Непредсказуемый ингредиент.", sell_price=150),
        Item(name="Карточка Мандрагоры", item_type="rare", rarity="legendary",
             description="Коллекционная редкость.", sell_price=500),

        # Расходники
        Item(name="Искра Роста", item_type="consumable", rarity="uncommon",
             description="Сбрасывает дневной лимит полива и добавляет роста.", sell_price=25),
    ]

    for item in items:
        existing = db.query(Item).filter(Item.name == item.name).first()
        if not existing:
            db.add(item)
            print(f"  📦 {item.name} добавлен")
        else:
            for key, value in item.__dict__.items():
                if not key.startswith("_") and key != "id":
                    setattr(existing, key, value)
            print(f"  🔄 {item.name} обновлён")

    db.commit()
    db.close()
    print("✅ Предметы в БД!")

if __name__ == "__main__":
    seed_items()
    