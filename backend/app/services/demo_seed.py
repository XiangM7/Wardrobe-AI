from __future__ import annotations

import base64
import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import CLOTHING_UPLOAD_DIR, PROFILE_UPLOAD_DIR
from app.models.clothing import ClothingItem
from app.models.profile import UserProfile
from app.models.user import User


DEMO_EMAIL = "demo@wardrobe-ai.local"
_PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9WlAb6UAAAAASUVORK5CYII="
)


def _write_seed_image(destination_dir: Path, prefix: str) -> str:
    destination_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{prefix}-{uuid.uuid4().hex[:10]}.png"
    file_path = destination_dir / filename
    file_path.write_bytes(_PIXEL_PNG)
    folder_name = destination_dir.name
    return f"uploads/{folder_name}/{filename}"


def _seed_clothing_items(db: Session, user_id: int) -> None:
    items = [
        {
            "category": "tops",
            "brand": "Uniqlo Air Tee",
            "primary_color": "white",
            "secondary_color": None,
            "style_tags": ["clean", "casual", "minimal"],
            "season_tags": ["spring", "summer"],
            "formality": "casual",
            "fit": "regular",
            "is_favorite": True,
        },
        {
            "category": "tops",
            "brand": "Navy Oxford Shirt",
            "primary_color": "navy",
            "secondary_color": None,
            "style_tags": ["clean", "smart-casual"],
            "season_tags": ["spring", "autumn"],
            "formality": "smart-casual",
            "fit": "regular",
            "is_favorite": False,
        },
        {
            "category": "tops",
            "brand": "Stone Overshirt",
            "primary_color": "beige",
            "secondary_color": None,
            "style_tags": ["minimal", "street"],
            "season_tags": ["autumn", "winter"],
            "formality": "casual",
            "fit": "relaxed",
            "is_favorite": False,
        },
        {
            "category": "pants",
            "brand": "Black Tapered Trousers",
            "primary_color": "black",
            "secondary_color": None,
            "style_tags": ["clean", "minimal", "smart-casual"],
            "season_tags": ["spring", "autumn", "winter"],
            "formality": "smart-casual",
            "fit": "slim",
            "is_favorite": True,
        },
        {
            "category": "pants",
            "brand": "Relaxed Khaki Pants",
            "primary_color": "beige",
            "secondary_color": None,
            "style_tags": ["casual", "minimal"],
            "season_tags": ["spring", "summer", "autumn"],
            "formality": "casual",
            "fit": "relaxed",
            "is_favorite": False,
        },
        {
            "category": "pants",
            "brand": "Dark Denim",
            "primary_color": "navy",
            "secondary_color": None,
            "style_tags": ["casual", "street"],
            "season_tags": ["spring", "autumn", "winter"],
            "formality": "casual",
            "fit": "regular",
            "is_favorite": False,
        },
        {
            "category": "shoes",
            "brand": "White Leather Sneakers",
            "primary_color": "white",
            "secondary_color": None,
            "style_tags": ["clean", "casual", "minimal"],
            "season_tags": ["spring", "summer", "autumn"],
            "formality": "casual",
            "fit": "regular",
            "is_favorite": True,
        },
        {
            "category": "shoes",
            "brand": "Black Derby Sneakers",
            "primary_color": "black",
            "secondary_color": None,
            "style_tags": ["clean", "smart-casual"],
            "season_tags": ["spring", "autumn", "winter"],
            "formality": "smart-casual",
            "fit": "regular",
            "is_favorite": False,
        },
    ]

    for item in items:
        db.add(
            ClothingItem(
                user_id=user_id,
                image_path=_write_seed_image(CLOTHING_UPLOAD_DIR, item["category"]),
                category=item["category"],
                primary_color=item["primary_color"],
                secondary_color=item["secondary_color"],
                style_tags=item["style_tags"],
                season_tags=item["season_tags"],
                formality=item["formality"],
                fit=item["fit"],
                brand=item["brand"],
                is_favorite=item["is_favorite"],
            )
        )


def seed_demo_user(db: Session) -> tuple[User, bool]:
    existing_user = db.scalar(select(User).where(User.email == DEMO_EMAIL))
    if existing_user:
        existing_profile = db.scalar(select(UserProfile).where(UserProfile.user_id == existing_user.id))
        if not existing_profile:
            db.add(
                UserProfile(
                    user_id=existing_user.id,
                    full_body_image_path=_write_seed_image(PROFILE_UPLOAD_DIR, "demo-profile"),
                    style_preferences=["clean", "casual", "minimal"],
                    body_goals=["look taller", "look cleaner", "more comfortable"],
                    color_preferences=["white", "navy", "black", "beige"],
                    avoid_tags=["itchy"],
                    notes="Demo profile for showcasing the wardrobe recommendation flow.",
                )
            )

        existing_items = list(db.scalars(select(ClothingItem).where(ClothingItem.user_id == existing_user.id)))
        if not existing_items:
            _seed_clothing_items(db, existing_user.id)

        db.commit()
        return existing_user, False

    user = User(name="Demo Closet", email=DEMO_EMAIL)
    db.add(user)
    db.flush()

    profile = UserProfile(
        user_id=user.id,
        full_body_image_path=_write_seed_image(PROFILE_UPLOAD_DIR, "demo-profile"),
        style_preferences=["clean", "casual", "minimal"],
        body_goals=["look taller", "look cleaner", "more comfortable"],
        color_preferences=["white", "navy", "black", "beige"],
        avoid_tags=["itchy"],
        notes="Demo profile for showcasing the wardrobe recommendation flow.",
    )
    db.add(profile)
    _seed_clothing_items(db, user.id)
    db.commit()
    db.refresh(user)
    return user, True
