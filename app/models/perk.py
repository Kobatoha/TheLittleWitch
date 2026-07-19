from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Perk(Base):
    """Перки (бонусы) игрока, открываемые за уровни."""
    __tablename__ = "perks"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    perk_code = Column(String(50), nullable=False)  # "double_water", "rare_luck_10", "extra_bed"
    perk_name = Column(String(100), nullable=False)  # "Двойной полив"
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    unlocked_at = Column(DateTime, server_default=func.now())

    player = relationship("Player", backref="perks")

    def __str__(self):
        return f"{self.perk_name} ({'активен' if self.is_active else 'неактивен'})"
        