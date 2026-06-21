from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    quantity = Column(Integer, default=1)
    quality = Column(String, default="Обычный")  # Увядший, Обычный, Сочный, Искрящийся
    source_bed_id = Column(Integer, ForeignKey("garden_beds.id"), nullable=True)  # с какой грядки собрано
    created_at = Column(DateTime, server_default=func.now())

    player = relationship("Player", backref="inventory_items")
    item = relationship("Item")
    source_bed = relationship("GardenBed", backref="harvested_items")

    def __str__(self):
        return f"{self.quantity}x {self.item.name} ({self.quality})"
        