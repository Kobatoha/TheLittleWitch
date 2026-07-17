from app.core.database import SessionLocal

from app.models.recipe import Recipe
from app.models.item import Item


def seed_recipes():
    db = SessionLocal()
    
    # Получаем предметы
    mandrake = db.query(Item).filter(Item.name == "Корень мандрагоры").first()
    dew = db.query(Item).filter(Item.name == "Капля утренней росы").first()
    lily = db.query(Item).filter(Item.name == "Лепесток лунной лилии").first()
    pollen = db.query(Item).filter(Item.name == "Волшебная пыльца").first()
    bog = db.query(Item).filter(Item.name == "Шипучка болотная").first()
    firefly = db.query(Item).filter(Item.name == "Крошечный светлячок").first()
    tear = db.query(Item).filter(Item.name == "Слеза феи").first()
    
    # Зелья
    vigor_potion = db.query(Item).filter(Item.name == "Зелье бодрости").first()
    lunar_elixir = db.query(Item).filter(Item.name == "Лунный эликсир").first()
    dark_brew = db.query(Item).filter(Item.name == "Тёмная настойка").first()
    vitality_essence = db.query(Item).filter(Item.name == "Эссенция живучести").first()
    
    recipes = []
    
    if mandrake and dew and vigor_potion:
        recipes.append(Recipe(
            name="Зелье бодрости",
            description="Корень мандрагоры + Утренняя роса. Классика ведьмовства.",
            ingredient_1_id=mandrake.id,
            ingredient_2_id=dew.id,
            result_item_id=vigor_potion.id,
            result_quantity=1,
            base_success_chance=100.0,
            quality_bonus_percent=10
        ))
    
    if lily and pollen and lunar_elixir:
        recipes.append(Recipe(
            name="Лунный эликсир",
            description="Лепесток лунной лилии + Волшебная пыльца. Ускоряет рост.",
            ingredient_1_id=lily.id,
            ingredient_2_id=pollen.id,
            result_item_id=lunar_elixir.id,
            result_quantity=1,
            base_success_chance=85.0,
            quality_bonus_percent=15
        ))
    
    if bog and firefly and dark_brew:
        recipes.append(Recipe(
            name="Тёмная настойка",
            description="Шипучка болотная + Светлячок. Защита от увядания.",
            ingredient_1_id=bog.id,
            ingredient_2_id=firefly.id,
            result_item_id=dark_brew.id,
            result_quantity=1,
            base_success_chance=70.0,
            quality_bonus_percent=20
        ))
    
    if mandrake and tear and vitality_essence:
        recipes.append(Recipe(
            name="Эссенция живучести",
            description="Корень мандрагоры + Слеза феи. Мощное восстановление.",
            ingredient_1_id=mandrake.id,
            ingredient_2_id=tear.id,
            result_item_id=vitality_essence.id,
            result_quantity=1,
            base_success_chance=90.0,
            quality_bonus_percent=10
        ))
    
    for r in recipes:
        existing = db.query(Recipe).filter(Recipe.name == r.name).first()
        if not existing:
            db.add(r)
            print(f"  📜 {r.name} добавлен")
        else:
            for key, value in r.__dict__.items():
                if not key.startswith("_") and key != "id":
                    setattr(existing, key, value)
            print(f"  🔄 {r.name} обновлён")
    
    db.commit()
    db.close()
    print("✅ Рецепты в БД!")

if __name__ == "__main__":
    seed_recipes()
