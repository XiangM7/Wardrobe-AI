from datetime import datetime

from pydantic import Field

from app.schemas.common import ORMModel


class UserProfileRead(ORMModel):
    id: int
    user_id: int
    full_body_image_path: str | None = None
    style_preferences: list[str] = Field(default_factory=list)
    body_goals: list[str] = Field(default_factory=list)
    color_preferences: list[str] = Field(default_factory=list)
    avoid_tags: list[str] = Field(default_factory=list)
    notes: str | None = None
    created_at: datetime
