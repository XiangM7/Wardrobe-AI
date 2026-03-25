from datetime import datetime

from app.schemas.common import ORMModel


class FeedbackCreate(ORMModel):
    outfit_id: int
    liked: bool = False
    saved: bool = False
    worn: bool = False
    feedback_text: str | None = None


class FeedbackRead(ORMModel):
    id: int
    user_id: int
    outfit_id: int
    liked: bool
    saved: bool
    worn: bool
    feedback_text: str | None = None
    created_at: datetime
