from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.feedback import UserFeedback
from app.schemas.feedback import FeedbackCreate, FeedbackRead
from app.services.feedback_service import save_feedback


router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.get("/{user_id}", response_model=list[FeedbackRead])
def list_feedback(user_id: int, db: Session = Depends(get_db)) -> list[UserFeedback]:
    return list(
        db.scalars(
            select(UserFeedback)
            .where(UserFeedback.user_id == user_id)
            .order_by(UserFeedback.created_at.desc())
        )
    )


@router.post("/{user_id}", response_model=FeedbackRead, status_code=status.HTTP_201_CREATED)
def create_feedback(
    user_id: int,
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
) -> FeedbackRead:
    return save_feedback(db=db, user_id=user_id, payload=payload)
