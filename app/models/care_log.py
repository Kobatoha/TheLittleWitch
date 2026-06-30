from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class CareLog(Base):
    __tablename__ = "care_logs"

    id = Column(Integer, primary_key=True, index=True)
    garden_bed_id = Column(Integer, ForeignKey("garden_beds.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    action = Column(String, nullable=False)          # "water", "clean", "spark", "moon", "daily", "harvest"
    action_name = Column(String, nullable=False)      # "Орошение лунной росой", "Очищение листьев"...
    effect = Column(String, nullable=True)            # "+5 живучести, +10 эссенции"
    mood = Column(String, default="neutral")          # "positive", "negative", "neutral"
    details = Column(String, nullable=True)           # "Найден радужный пучеглаз!"
    created_at = Column(DateTime, server_default=func.now())

    garden_bed = relationship("GardenBed", backref="care_logs")
    player = relationship("Player", backref="care_logs")

    def __str__(self):
        return f"[{self.action}] {self.action_name} — {self.effect}"
