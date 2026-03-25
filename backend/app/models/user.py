from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    profile: Mapped["UserProfile | None"] = relationship(
        "UserProfile",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    clothing_items: Mapped[list["ClothingItem"]] = relationship(
        "ClothingItem",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    recommendation_requests: Mapped[list["RecommendationRequest"]] = relationship(
        "RecommendationRequest",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    outfit_recommendations: Mapped[list["OutfitRecommendation"]] = relationship(
        "OutfitRecommendation",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    feedback_entries: Mapped[list["UserFeedback"]] = relationship(
        "UserFeedback",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    try_on_previews: Mapped[list["TryOnPreview"]] = relationship(
        "TryOnPreview",
        back_populates="user",
        cascade="all, delete-orphan",
    )
