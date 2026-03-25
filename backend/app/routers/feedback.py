from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.feedback import UserFeedback
from app.models.recommendation import OutfitRecommendation
from app.models.user import User
from app.schemas.feedback import FeedbackCreate, FeedbackRead


router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/{user_id}", response_model=FeedbackRead, status_code=status.HTTP_201_CREATED)
def create_feedback(
    user_id: int,
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
) -> UserFeedback:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    outfit = db.get(OutfitRecommendation, payload.outfit_id)
    if not outfit or outfit.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit recommendation not found.")

    feedback = UserFeedback(
        user_id=user_id,
        outfit_id=payload.outfit_id,
        liked=payload.liked,
        saved=payload.saved,
        worn=payload.worn,
        feedback_text=(payload.feedback_text or "").strip() or None,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback
