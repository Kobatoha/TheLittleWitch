from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.core import config
from app.core import balance
from app.game.formulas import get_stage_name, can_level_up


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
    last_cleaned_at = Column(DateTime, nullable=True)  # когда последний раз пололи
    last_harvested_at = Column(DateTime, nullable=True)     # когда последний раз собирали
    recovery_until = Column(DateTime, nullable=True)        # до какого времени растение восстанавливается
    last_daily_update = Column(DateTime, nullable=True)  # когда было последнее ежедневное обновление
    
    planted_at = Column(DateTime, server_default=func.now())  # когда посадили (для истории)
    created_at = Column(DateTime, server_default=func.now())

    player = relationship("Player", back_populates="garden_beds")
    plant = relationship("Plant", back_populates="garden_beds")

    @property
    def stage_name(self) -> str:
        return get_stage_name(self.growth_stage)

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
        if self.recovery_until and self.recovery_until > datetime.utcnow():
            return False
        # В Зените (100%) поливать можно!
        if self.last_watered_at:
            return self.last_watered_at.date() < datetime.utcnow().date()
        return True

    @property
    def can_harvest(self) -> bool:
        if self.is_dead:
            return False
        if self.plant_id is None:
            return False
        if self.recovery_until and self.recovery_until > datetime.utcnow():
            return False
        return self.growth_stage >= balance.MIN_HARVEST_STAGE

    @property
    def is_in_zenith(self) -> bool:
        return self.growth_stage >= 100
            
    @property
    def hours_until_next_update(self) -> int:
        if not self.last_daily_update:
            return 0
        next_update = self.last_daily_update + timedelta(hours=balance.HOURS_BETWEEN_UPDATES)
        delta = next_update - datetime.utcnow()
        return max(0, int(delta.total_seconds() / 3600))
    
    @property
    def can_clean(self) -> bool:
        """Можно ли полоть: не умерло, не на восстановлении, не использовано сегодня."""
        if self.is_dead:
            return False
        if self.plant_id is None:
            return False
        if self.recovery_until and self.recovery_until > datetime.utcnow():
            return False
        if self.last_cleaned_at and self.last_cleaned_at.date() >= datetime.utcnow().date():
            return False
        return True
        