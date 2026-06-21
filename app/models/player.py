from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,  # один пользователь — один игрок
        index=True,
        nullable=False
    )

    # Игровой ник (может отличаться от логина!)
    nickname: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    # Ресурсы
    coins: Mapped[int] = mapped_column(Integer, default=100)
    energy: Mapped[int] = mapped_column(Integer, default=100)
    max_energy: Mapped[int] = mapped_column(Integer, default=100)

    # Прогресс
    level: Mapped[int] = mapped_column(Integer, default=1)
    experience: Mapped[int] = mapped_column(Integer, default=0)
    days_in_game: Mapped[int] = mapped_column(Integer, default=0)

    # Внешность (JSON со слоями — будет потом)
    appearance: Mapped[str] = mapped_column(String(2000), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Связь обратно к User
    user: Mapped["User"] = relationship("User", back_populates="player")

    # Связь с грядками (один-ко-многим)
    garden_beds = relationship("GardenBed", back_populates="player")

    def __str__(self) -> str:
        return f"{self.nickname} (lvl {self.level})"
        