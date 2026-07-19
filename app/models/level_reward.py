from sqlalchemy import Column, Integer, String

from app.core.database import Base


class LevelReward(Base):
    """Награды за достижение уровня."""
    __tablename__ = "level_rewards"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(Integer, unique=True, nullable=False)
    reward_type = Column(String(50), nullable=False)  # "perk", "coins", "unlock_recipe", "title"
    reward_code = Column(String(100), nullable=True)   # "double_water", "rare_luck_10"
    reward_name = Column(String(200), nullable=False)   # "Двойной полив"
    description = Column(String(300), nullable=True)
    reward_value = Column(Integer, default=0)           # монеты, % бонуса и т.д.

    def __str__(self):
        return f"Ур.{self.level}: {self.reward_name}"
        