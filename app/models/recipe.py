from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.core.database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)                    # "Зелье бодрости"
    description = Column(String, nullable=True)
    
    # Три слота для ингредиентов (0 = не используется)
    ingredient_1_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    ingredient_2_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    ingredient_3_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    
    # Результат
    result_item_id = Column(Integer, ForeignKey("items.id"), nullable=False)  # что получится
    result_quantity = Column(Integer, default=1)                              # сколько штук
    
    # Шанс успеха (базовый)
    base_success_chance = Column(Float, default=100.0)  # 100 = всегда, 70 = 70%
    
    # Бонус качества от качества ингредиентов
    quality_bonus_percent = Column(Integer, default=0)  # на сколько % повышается шанс успеха
    
    ingredient_1 = relationship("Item", foreign_keys=[ingredient_1_id])
    ingredient_2 = relationship("Item", foreign_keys=[ingredient_2_id])
    ingredient_3 = relationship("Item", foreign_keys=[ingredient_3_id])
    result_item = relationship("Item", foreign_keys=[result_item_id])

    def __str__(self):
        return self.name
