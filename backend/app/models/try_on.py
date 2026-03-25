from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TryOnPreview(Base):
    __tablename__ = "try_on_previews"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    outfit_id: Mapped[int] = mapped_column(ForeignKey("outfit_recommendations.id"), index=True)
    provider: Mapped[str] = mapped_column(String(64))
    preview_image_path: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="try_on_previews")
    outfit: Mapped["OutfitRecommendation"] = relationship("OutfitRecommendation", back_populates="try_on_previews")
