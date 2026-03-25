from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ClothingItem(Base):
    __tablename__ = "clothing_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    image_path: Mapped[str]
    category: Mapped[str] = mapped_column(String(32), index=True)
    primary_color: Mapped[str | None] = mapped_column(String(64))
    secondary_color: Mapped[str | None] = mapped_column(String(64))
    style_tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    season_tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    formality: Mapped[str | None] = mapped_column(String(32))
    fit: Mapped[str | None] = mapped_column(String(32))
    brand: Mapped[str | None] = mapped_column(String(120))
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    last_worn_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="clothing_items")
