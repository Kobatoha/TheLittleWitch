from sqlalchemy import Column, Integer, String, ForeignKey

from app.core.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    item_type = Column(String, nullable=False)  # "ingredient", "bonus", "rare", "seed"
    rarity = Column(String, default="common")   # "common", "uncommon", "rare", "epic", "legendary"
    description = Column(String, nullable=True)
    potency_boost = Column(Integer, default=0)  # бонус к Силе Рода (для семян)
    icon = Column(String, nullable=True)
    sell_price = Column(Integer, default=10)
    linked_plant_id = Column(Integer, ForeignKey("plants.id"), nullable=True)

    def __str__(self):
        return f"{self.name} ({self.item_type}, {self.rarity})"
