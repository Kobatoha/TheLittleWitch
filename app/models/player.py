from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False
    )

    # === ОСНОВНОЕ ===
    nickname: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    coins: Mapped[int] = mapped_column(Integer, default=100)
    energy: Mapped[int] = mapped_column(Integer, default=100)
    max_energy: Mapped[int] = mapped_column(Integer, default=100)
    appearance: Mapped[str] = mapped_column(String(2000), nullable=True)

    # === ПРОГРЕСС ===
    level: Mapped[int] = mapped_column(Integer, default=1)
    experience : Mapped[int] = mapped_column(Integer, default=0)
    experience_to_next: Mapped[int] = mapped_column(Integer, default=100)

    # === ТИТУЛЫ ===
    title: Mapped[str] = mapped_column(String(100), nullable=True)

    # === СТАТИСТИКА ===
    total_harvests: Mapped[int] = mapped_column(Integer, default=0)
    total_potions_brewed: Mapped[int] = mapped_column(Integer, default=0)
    total_coins_earned: Mapped[int] = mapped_column(Integer, default=0)
    total_moon_baths: Mapped[int] = mapped_column(Integer, default=0)
    days_in_game: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # === СВЯЗИ ===
    user: Mapped["User"] = relationship("User", back_populates="player")
    garden_beds = relationship("GardenBed", back_populates="player")

    def __str__(self) -> str:
        return f"{self.nickname} (lvl {self.level})"

    @property
    def xp_progress_percent(self) -> int:
        if self.xp_to_next == 0:
            return 100
        return min(100, int(self.xp / self.xp_to_next * 100))

    @property
    def title_display(self) -> str:
        return self.title or "Начинающая травница"
