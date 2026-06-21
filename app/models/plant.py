from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship

from app.core.database import Base

class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    icon = Column(String, nullable=True)

    # === СТАРАЯ СИСТЕМА (пока оставляем) ===
    growth_time = Column(Integer, nullable=True)       # минуты до созревания
    water_bonus = Column(Integer, nullable=True)       # ускорение от полива (мин)
    base_harvest_count = Column(Integer, default=1)    # сколько плодов при сборе

    # === НОВАЯ СИСТЕМА ===
    base_vitality = Column(Integer, default=100)       # стартовая Живучесть
    vitality_decay = Column(Integer, default=5)        # потеря Живучести в час без ухода
    essence_per_care = Column(Integer, default=12)     # +Эссенции за действие ухода
    growth_per_care = Column(Integer, default=8)       # +% Цикла Роста за действие ухода
    min_harvest_stage = Column(Integer, default=60)    # мин. стадия для сбора (Бутон)
    base_potency = Column(Integer, default=100)        # Сила Рода (пока константа)

    garden_beds = relationship("GardenBed", back_populates="plant")

    def __str__(self) -> str:
        return self.name
        