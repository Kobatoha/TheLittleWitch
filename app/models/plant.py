from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base

class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    icon_seed = Column(String, nullable=True)
    icon_sprout = Column(String, nullable=True)
    icon_stem = Column(String, nullable=True)
    icon_bud = Column(String, nullable=True)
    icon_bloom = Column(String, nullable=True)
    icon_mature = Column(String, nullable=True)

    # Параметры роста
    base_vitality = Column(Integer, default=100)       # стартовая Живучесть
    vitality_decay = Column(Integer, default=5)        # потеря Живучести в час без ухода
    essence_per_care = Column(Integer, default=12)     # +Эссенции за действие ухода
    growth_per_care = Column(Integer, default=8)       # +% Цикла Роста за действие ухода
    min_harvest_stage = Column(Integer, default=60)    # мин. стадия для сбора (Бутон)
    base_potency = Column(Integer, default=100)        # Сила Рода (пока константа)

    harvest_item_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    harvest_item = relationship("Item", foreign_keys=[harvest_item_id])

    garden_beds = relationship("GardenBed", back_populates="plant")

    def __str__(self) -> str:
        return self.name
        
    def get_icon_for_stage(self, growth_stage: int) -> str | None:
        if growth_stage >= 100:
            return self.icon_mature
        elif growth_stage >= 80:
            return self.icon_bloom
        elif growth_stage >= 60:
            return self.icon_bud
        elif growth_stage >= 40:
            return self.icon_stem
        elif growth_stage >= 20:
            return self.icon_sprout
        else:
            return self.icon_seed
