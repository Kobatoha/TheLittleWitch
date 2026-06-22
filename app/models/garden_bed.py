from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.core import config


class GardenBed(Base):
    __tablename__ = "garden_beds"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=True)

    # Новая система роста
    vitality = Column(Integer, default=100)            # Живучесть (0 = смерть)
    essence = Column(Integer, default=0)               # Эссенция (растёт от ухода)
    growth_stage = Column(Integer, default=0)          # Цикл Роста: 0-100

    # Восстановление и лимиты
    last_watered_at = Column(DateTime, nullable=True)      # когда последний раз поливали
    last_harvested_at = Column(DateTime, nullable=True)     # когда последний раз собирали
    recovery_until = Column(DateTime, nullable=True)        # до какого времени растение восстанавливается
    last_daily_update = Column(DateTime, nullable=True)  # когда было последнее ежедневное обновление
    
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
    def plant_name(self) -> str:
        return self.plant.name if self.plant else "—"

    def __str__(self) -> str:
        return f"Грядка {self.id} — {self.plant_name}"

    @property
    def can_water(self) -> bool:
        if self.is_dead:
            return False
        if self.plant_id is None:
            return False
        if self.growth_stage >= 100:  # Зрелость — поливать нельзя
            return False
        if self.recovery_until and self.recovery_until > datetime.utcnow():
            return False
        if self.last_watered_at:
            return self.last_watered_at.date() < datetime.utcnow().date()
        return True

    @property
    def can_harvest(self) -> bool:
        """Можно ли собирать."""
        if self.is_dead:
            return False
        if self.plant_id is None:
            return False
        if self.recovery_until and self.recovery_until > datetime.utcnow():
            return False
        return self.growth_stage >= (self.plant.min_harvest_stage if self.plant else 60)    
            
    @property
    def hours_until_next_update(self) -> int:
        """Сколько часов осталось до следующего ежедневного обновления."""
        if not self.last_daily_update:
            return 0
        next_update = self.last_daily_update + timedelta(hours=config.RECOVERY_HOURS)
        delta = next_update - datetime.utcnow()
        return max(0, int(delta.total_seconds() / 3600))
