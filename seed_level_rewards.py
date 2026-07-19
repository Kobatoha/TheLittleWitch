from app.core.database import SessionLocal

from app.models.level_reward import LevelReward


def seed_level_rewards():
    db = SessionLocal()
    rewards = [
        LevelReward(level=2, reward_type="perk", reward_code="inventory_slot", reward_name="+1 слот в инвентаре", description="Максимум предметов увеличен на 1"),
        LevelReward(level=3, reward_type="unlock_recipe", reward_code="recipe_vigor", reward_name="Рецепт: Зелье бодрости", description="Открывает рецепт Зелья бодрости"),
        LevelReward(level=5, reward_type="perk", reward_code="extra_bed", reward_name="+1 кадка в саду", description="Можно посадить на 1 растение больше"),
        LevelReward(level=7, reward_type="perk", reward_code="double_water", reward_name="Двойной полив", description="Можно поливать растения 2 раза в день"),
        LevelReward(level=10, reward_type="perk", reward_code="rare_luck_10", reward_name="+10% шанс редкой удачи", description="Шанс редкой удачи при сборе увеличен на 10%"),
        LevelReward(level=15, reward_type="perk", reward_code="strong_clean", reward_name="Сильная прополка", description="Прополка даёт +10 живучести вместо +5"),
        LevelReward(level=20, reward_type="coins", reward_code=None, reward_name="500 монет", description="Награда монетами", reward_value=500),
        LevelReward(level=25, reward_type="perk", reward_code="market_bonus_20", reward_name="+20% к цене продажи", description="Все предметы продаются на 20% дороже"),
        LevelReward(level=30, reward_type="title", reward_code="master_herbalist", reward_name="Титул: Мастер-травница", description="Новый титул в профиле"),
        LevelReward(level=50, reward_type="title", reward_code="supreme_witch", reward_name="Титул: Верховная Ведьма", description="Легендарный титул"),
    ]
    for r in rewards:
        existing = db.query(LevelReward).filter(LevelReward.level == r.level).first()
        if not existing:
            db.add(r)
    db.commit()
    db.close()
    print("✅ Награды за уровни в БД!")

if __name__ == "__main__":
    seed_level_rewards()
