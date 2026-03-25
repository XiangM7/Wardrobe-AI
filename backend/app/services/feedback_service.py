from __future__ import annotations

from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.feedback import UserFeedback
from app.models.recommendation import OutfitRecommendation
from app.models.user import User
from app.schemas.feedback import FeedbackCreate


def save_feedback(db: Session, user_id: int, payload: FeedbackCreate) -> UserFeedback:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    outfit = db.get(OutfitRecommendation, payload.outfit_id)
    if not outfit or outfit.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit recommendation not found.")

    feedback = db.scalar(
        select(UserFeedback).where(
            UserFeedback.user_id == user_id,
            UserFeedback.outfit_id == payload.outfit_id,
        )
    )
    if feedback:
        feedback.liked = payload.liked
        feedback.saved = payload.saved
        feedback.worn = payload.worn
        feedback.feedback_text = (payload.feedback_text or "").strip() or None
    else:
        feedback = UserFeedback(
            user_id=user_id,
            outfit_id=payload.outfit_id,
            liked=payload.liked,
            saved=payload.saved,
            worn=payload.worn,
            feedback_text=(payload.feedback_text or "").strip() or None,
        )
        db.add(feedback)

    if payload.worn:
        worn_on = date.today()
        for item in [outfit.top_item, outfit.pants_item, outfit.shoes_item]:
            item.last_worn_date = worn_on

    db.commit()
    db.refresh(feedback)
    return feedback
