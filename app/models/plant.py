from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base

class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)        # "Мандрагора"
    growth_time = Column(Integer, nullable=False)             # в минутах
    water_bonus = Column(Integer, default=30)                 # на сколько ускоряет полив (мин)
    base_harvest_count = Column(Integer, default=1)           # сколько плодов при сборе
    icon = Column(String, nullable=True)                      # путь к картинке (потом)
    description = Column(String, nullable=True)

    def __str__(self) -> str:
        return self.name
