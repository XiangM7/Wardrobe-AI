from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.feedback import FeedbackCreate, FeedbackRead
from app.services.feedback_service import save_feedback


router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/{user_id}", response_model=FeedbackRead, status_code=status.HTTP_201_CREATED)
def create_feedback(
    user_id: int,
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
) -> FeedbackRead:
    return save_feedback(db=db, user_id=user_id, payload=payload)
