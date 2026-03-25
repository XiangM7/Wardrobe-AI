from __future__ import annotations

from itertools import product

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.clothing import ClothingItem
from app.models.profile import UserProfile
from app.models.recommendation import OutfitRecommendation, RecommendationRequest
from app.models.user import User
from app.services.explanations import generate_explanation
from app.services.scoring import calculate_outfit_score, is_valid_combination


def _load_user_context(db: Session, user_id: int) -> tuple[User, UserProfile | None, list[ClothingItem]]:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    profile = db.scalar(select(UserProfile).where(UserProfile.user_id == user_id))
    items = list(
        db.scalars(select(ClothingItem).where(ClothingItem.user_id == user_id).order_by(ClothingItem.created_at.desc()))
    )
    return user, profile, items


def generate_recommendations(
    db: Session,
    user_id: int,
    target_style: str,
    target_scene: str,
    weather: str,
    extra_note: str | None,
) -> tuple[RecommendationRequest, list[OutfitRecommendation]]:
    _, profile, items = _load_user_context(db, user_id)

    tops = [item for item in items if item.category == "tops"]
    pants = [item for item in items if item.category == "pants"]
    shoes = [item for item in items if item.category == "shoes"]

    if not tops or not pants or not shoes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You need at least one top, one pair of pants, and one pair of shoes before requesting outfits.",
        )

    request_record = RecommendationRequest(
        user_id=user_id,
        target_style=target_style.strip(),
        target_scene=target_scene.strip(),
        weather=weather.strip(),
        extra_note=(extra_note or "").strip() or None,
    )
    db.add(request_record)
    db.flush()

    candidates: list[tuple[float, OutfitRecommendation]] = []
    for top_item, pants_item, shoes_item in product(tops, pants, shoes):
        if not is_valid_combination(top_item, pants_item, shoes_item, request_record):
            continue

        score = calculate_outfit_score(top_item, pants_item, shoes_item, profile, request_record)
        explanation = generate_explanation(top_item, pants_item, shoes_item, profile, request_record, score)
        recommendation = OutfitRecommendation(
            request_id=request_record.id,
            user_id=user_id,
            top_item_id=top_item.id,
            pants_item_id=pants_item.id,
            shoes_item_id=shoes_item.id,
            total_score=score.total_score,
            compatibility_score=score.compatibility_score,
            user_fit_score=score.user_fit_score,
            style_match_score=score.style_match_score,
            scene_match_score=score.scene_match_score,
            weather_match_score=score.weather_match_score,
            preference_score=score.preference_score,
            repetition_penalty=score.repetition_penalty,
            reason_text=explanation,
        )
        recommendation.top_item = top_item
        recommendation.pants_item = pants_item
        recommendation.shoes_item = shoes_item
        candidates.append((score.total_score, recommendation))

    if not candidates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid outfit combinations matched the current closet and request.",
        )

    top_recommendations = [recommendation for _, recommendation in sorted(candidates, key=lambda entry: entry[0], reverse=True)[:3]]
    for recommendation in top_recommendations:
        db.add(recommendation)

    db.commit()
    db.refresh(request_record)

    recommendation_ids = [recommendation.id for recommendation in top_recommendations]
    hydrated_recommendations = list(
        db.scalars(
            select(OutfitRecommendation)
            .where(OutfitRecommendation.id.in_(recommendation_ids))
            .options(
                joinedload(OutfitRecommendation.top_item),
                joinedload(OutfitRecommendation.pants_item),
                joinedload(OutfitRecommendation.shoes_item),
            )
            .order_by(OutfitRecommendation.total_score.desc())
        )
    )
    return request_record, hydrated_recommendations


def get_recommendation_history(db: Session, user_id: int) -> list[RecommendationRequest]:
    return list(
        db.scalars(
            select(RecommendationRequest)
            .where(RecommendationRequest.user_id == user_id)
            .options(
                selectinload(RecommendationRequest.outfits).joinedload(OutfitRecommendation.top_item),
                selectinload(RecommendationRequest.outfits).joinedload(OutfitRecommendation.pants_item),
                selectinload(RecommendationRequest.outfits).joinedload(OutfitRecommendation.shoes_item),
            )
            .order_by(RecommendationRequest.created_at.desc())
        )
    )
