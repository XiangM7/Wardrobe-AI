from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RecommendationRequest(Base):
    __tablename__ = "recommendation_requests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    target_style: Mapped[str] = mapped_column(String(64))
    target_scene: Mapped[str] = mapped_column(String(64))
    weather: Mapped[str] = mapped_column(String(32))
    extra_note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="recommendation_requests")
    outfits: Mapped[list["OutfitRecommendation"]] = relationship(
        "OutfitRecommendation",
        back_populates="request",
        cascade="all, delete-orphan",
    )


class OutfitRecommendation(Base):
    __tablename__ = "outfit_recommendations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("recommendation_requests.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    top_item_id: Mapped[int] = mapped_column(ForeignKey("clothing_items.id"))
    pants_item_id: Mapped[int] = mapped_column(ForeignKey("clothing_items.id"))
    shoes_item_id: Mapped[int] = mapped_column(ForeignKey("clothing_items.id"))
    total_score: Mapped[float] = mapped_column(Float)
    compatibility_score: Mapped[float] = mapped_column(Float)
    user_fit_score: Mapped[float] = mapped_column(Float)
    style_match_score: Mapped[float] = mapped_column(Float)
    scene_match_score: Mapped[float] = mapped_column(Float)
    weather_match_score: Mapped[float] = mapped_column(Float)
    preference_score: Mapped[float] = mapped_column(Float)
    repetition_penalty: Mapped[float] = mapped_column(Float)
    reason_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    request: Mapped["RecommendationRequest"] = relationship("RecommendationRequest", back_populates="outfits")
    user: Mapped["User"] = relationship("User", back_populates="outfit_recommendations")
    top_item: Mapped["ClothingItem"] = relationship("ClothingItem", foreign_keys=[top_item_id], lazy="joined")
    pants_item: Mapped["ClothingItem"] = relationship("ClothingItem", foreign_keys=[pants_item_id], lazy="joined")
    shoes_item: Mapped["ClothingItem"] = relationship("ClothingItem", foreign_keys=[shoes_item_id], lazy="joined")
    feedback_entries: Mapped[list["UserFeedback"]] = relationship(
        "UserFeedback",
        back_populates="outfit",
        cascade="all, delete-orphan",
    )
