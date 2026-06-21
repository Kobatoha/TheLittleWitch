from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class GardenBed(Base):
    __tablename__ = "garden_beds"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)  # ← было users.id
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=True)  # None = пустая грядка

    # Тайминг
    planted_at = Column(DateTime, nullable=True)      # когда посадили
    ready_at = Column(DateTime, nullable=True)        # когда созреет

    # Состояние
    moisture = Column(Integer, default=0)             # 0-100, влажность
    times_watered = Column(Integer, default=0)        # сколько раз полили

    created_at = Column(DateTime, server_default=func.now())

    # Отношения
    player = relationship("Player", back_populates="garden_beds")
    plant = relationship("Plant", back_populates="garden_beds")

    def __str__(self) -> str:
        return f"Грядка {self.id} для {self.player.username}"

    @property
    def plant_name(self):
        return self.plant.name if self.plant else "—"
