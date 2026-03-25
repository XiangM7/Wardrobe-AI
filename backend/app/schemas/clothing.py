from datetime import date, datetime

from pydantic import Field

from app.schemas.common import ORMModel


class ClothingItemUpdate(ORMModel):
    category: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    style_tags: list[str] | None = None
    season_tags: list[str] | None = None
    formality: str | None = None
    fit: str | None = None
    brand: str | None = None
    is_favorite: bool | None = None
    last_worn_date: date | None = None


class ClothingItemRead(ORMModel):
    id: int
    user_id: int
    image_path: str
    category: str
    primary_color: str | None = None
    secondary_color: str | None = None
    style_tags: list[str] = Field(default_factory=list)
    season_tags: list[str] = Field(default_factory=list)
    formality: str | None = None
    fit: str | None = None
    brand: str | None = None
    is_favorite: bool = False
    last_worn_date: date | None = None
    created_at: datetime
