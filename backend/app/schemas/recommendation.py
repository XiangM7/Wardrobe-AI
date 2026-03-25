from datetime import datetime

from app.schemas.clothing import ClothingItemRead
from app.schemas.common import ORMModel
from app.schemas.feedback import FeedbackRead
from app.schemas.try_on import TryOnPreviewRead


class RecommendationRequestCreate(ORMModel):
    target_style: str
    target_scene: str
    weather: str
    extra_note: str | None = None


class RecommendationRequestRead(ORMModel):
    id: int
    user_id: int
    target_style: str
    target_scene: str
    weather: str
    extra_note: str | None = None
    created_at: datetime


class OutfitRecommendationRead(ORMModel):
    id: int
    request_id: int
    user_id: int
    top_item_id: int
    pants_item_id: int
    shoes_item_id: int
    total_score: float
    compatibility_score: float
    user_fit_score: float
    style_match_score: float
    scene_match_score: float
    weather_match_score: float
    preference_score: float
    repetition_penalty: float
    reason_text: str
    created_at: datetime
    top_item: ClothingItemRead
    pants_item: ClothingItemRead
    shoes_item: ClothingItemRead
    feedback: FeedbackRead | None = None
    latest_try_on_preview: TryOnPreviewRead | None = None


class RecommendationResponse(ORMModel):
    request: RecommendationRequestRead
    recommendations: list[OutfitRecommendationRead]


class RecommendationHistoryEntry(ORMModel):
    request: RecommendationRequestRead
    recommendations: list[OutfitRecommendationRead]
