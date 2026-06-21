from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class GardenBed(Base):
    __tablename__ = "garden_beds"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=True)

    # Новая система роста
    vitality = Column(Integer, default=100)            # Живучесть (0 = смерть)
    essence = Column(Integer, default=0)               # Эссенция (растёт от ухода)
    growth_stage = Column(Integer, default=0)          # Цикл Роста: 0-100

    planted_at = Column(DateTime, server_default=func.now())  # когда посадили (для истории)
    created_at = Column(DateTime, server_default=func.now())

    player = relationship("Player", back_populates="garden_beds")
    plant = relationship("Plant", back_populates="garden_beds")

    @property
    def stage_name(self) -> str:
        stages = [
            (0, "Семя"),
            (20, "Росток"),
            (40, "Стебель"),
            (60, "Бутон"),
            (80, "Цветение"),
            (100, "Зрелость"),
        ]
        for threshold, name in reversed(stages):
            if self.growth_stage >= threshold:
                return name
        return "Семя"

    @property
    def is_dead(self) -> bool:
        return self.vitality <= 0

    @property
    def can_harvest(self) -> bool:
        return self.growth_stage >= self.plant.min_harvest_stage if self.plant else False

    @property
    def plant_name(self) -> str:
        return self.plant.name if self.plant else "—"

    def __str__(self) -> str:
        return f"Грядка {self.id} — {self.plant_name}"
        