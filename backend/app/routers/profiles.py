from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import PROFILE_UPLOAD_DIR, UPLOAD_DIR
from app.database import get_db
from app.models.profile import UserProfile
from app.models.user import User
from app.schemas.profile import UserProfileRead
from app.services.storage import remove_file, save_upload_file


router = APIRouter(prefix="/profiles", tags=["profiles"])


def parse_csv_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


@router.post("/{user_id}", response_model=UserProfileRead)
def upsert_profile(
    user_id: int,
    style_preferences: str | None = Form(None),
    body_goals: str | None = Form(None),
    color_preferences: str | None = Form(None),
    avoid_tags: str | None = Form(None),
    notes: str | None = Form(None),
    full_body_image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
) -> UserProfile:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    profile = db.scalar(select(UserProfile).where(UserProfile.user_id == user_id))
    image_path: str | None = profile.full_body_image_path if profile else None

    if full_body_image:
        if image_path:
            remove_file(image_path, UPLOAD_DIR)
        image_path = save_upload_file(full_body_image, PROFILE_UPLOAD_DIR, "uploads/profile_images")

    if profile:
        profile.full_body_image_path = image_path
        profile.style_preferences = parse_csv_list(style_preferences)
        profile.body_goals = parse_csv_list(body_goals)
        profile.color_preferences = parse_csv_list(color_preferences)
        profile.avoid_tags = parse_csv_list(avoid_tags)
        profile.notes = (notes or "").strip() or None
    else:
        profile = UserProfile(
            user_id=user_id,
            full_body_image_path=image_path,
            style_preferences=parse_csv_list(style_preferences),
            body_goals=parse_csv_list(body_goals),
            color_preferences=parse_csv_list(color_preferences),
            avoid_tags=parse_csv_list(avoid_tags),
            notes=(notes or "").strip() or None,
        )
        db.add(profile)

    db.commit()
    db.refresh(profile)
    return profile


@router.get("/{user_id}", response_model=UserProfileRead)
def get_profile(user_id: int, db: Session = Depends(get_db)) -> UserProfile:
    profile = db.scalar(select(UserProfile).where(UserProfile.user_id == user_id))
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")
    return profile
