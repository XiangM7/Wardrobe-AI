from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.recommendation import (
    RecommendationHistoryEntry,
    RecommendationRequestCreate,
    RecommendationResponse,
)
from app.services.recommendation_engine import generate_recommendations, get_recommendation_history


router = APIRouter(prefix="/recommend", tags=["recommendations"])


@router.post("/{user_id}", response_model=RecommendationResponse)
def create_recommendation_bundle(
    user_id: int,
    payload: RecommendationRequestCreate,
    db: Session = Depends(get_db),
) -> RecommendationResponse:
    request_record, recommendations = generate_recommendations(
        db=db,
        user_id=user_id,
        target_style=payload.target_style,
        target_scene=payload.target_scene,
        weather=payload.weather,
        extra_note=payload.extra_note,
    )
    return RecommendationResponse(request=request_record, recommendations=recommendations)


@router.get("/history/{user_id}", response_model=list[RecommendationHistoryEntry])
def recommendation_history(user_id: int, db: Session = Depends(get_db)) -> list[RecommendationHistoryEntry]:
    history = get_recommendation_history(db, user_id)
    return [
        RecommendationHistoryEntry(
            request=request_record,
            recommendations=sorted(request_record.outfits, key=lambda outfit: outfit.total_score, reverse=True),
        )
        for request_record in history
    ]
