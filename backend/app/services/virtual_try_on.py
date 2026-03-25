from __future__ import annotations

import base64
from html import escape
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.config import TRY_ON_UPLOAD_DIR, UPLOAD_DIR, VIRTUAL_TRY_ON_PROVIDER
from app.models.profile import UserProfile
from app.models.recommendation import OutfitRecommendation
from app.models.try_on import TryOnPreview
from app.models.user import User


def _to_data_uri(relative_path: str) -> str:
    file_path = UPLOAD_DIR / relative_path.replace("uploads/", "", 1)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Referenced preview asset is missing: {relative_path}",
        )

    mime_type = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(file_path.suffix.lower(), "application/octet-stream")
    encoded = base64.b64encode(file_path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _render_mock_svg_preview(profile_image_path: str, outfit: OutfitRecommendation) -> str:
    profile_href = _to_data_uri(profile_image_path)
    top_href = _to_data_uri(outfit.top_item.image_path)
    pants_href = _to_data_uri(outfit.pants_item.image_path)
    shoes_href = _to_data_uri(outfit.shoes_item.image_path)
    title = escape(
        f"{outfit.request.target_style} for {outfit.request.target_scene} - Wardrobe AI Try-On Preview"
    )
    reason = escape(outfit.reason_text)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 1200" role="img" aria-label="{title}">
  <defs>
    <linearGradient id="overlay" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="rgba(18,24,28,0.00)" />
      <stop offset="100%" stop-color="rgba(18,24,28,0.72)" />
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="16" stdDeviation="18" flood-color="rgba(20,26,31,0.28)" />
    </filter>
    <clipPath id="topClip"><rect x="285" y="190" width="330" height="270" rx="34" /></clipPath>
    <clipPath id="pantsClip"><rect x="305" y="445" width="290" height="315" rx="34" /></clipPath>
    <clipPath id="shoesClip"><rect x="280" y="760" width="340" height="120" rx="34" /></clipPath>
  </defs>

  <rect width="900" height="1200" fill="#efe6d9" />
  <image href="{escape(profile_href)}" x="0" y="0" width="900" height="1200" preserveAspectRatio="xMidYMid slice" />
  <rect width="900" height="1200" fill="url(#overlay)" />

  <g filter="url(#shadow)">
    <rect x="58" y="58" width="784" height="1084" rx="40" fill="none" stroke="rgba(255,255,255,0.28)" stroke-width="2" />
  </g>

  <g opacity="0.76">
    <rect x="275" y="180" width="350" height="290" rx="38" fill="rgba(255,255,255,0.12)" />
    <image href="{escape(top_href)}" x="285" y="190" width="330" height="270" preserveAspectRatio="xMidYMid meet" clip-path="url(#topClip)" />

    <rect x="295" y="435" width="310" height="335" rx="38" fill="rgba(255,255,255,0.10)" />
    <image href="{escape(pants_href)}" x="305" y="445" width="290" height="315" preserveAspectRatio="xMidYMid meet" clip-path="url(#pantsClip)" />

    <rect x="270" y="750" width="360" height="140" rx="38" fill="rgba(255,255,255,0.10)" />
    <image href="{escape(shoes_href)}" x="280" y="760" width="340" height="120" preserveAspectRatio="xMidYMid meet" clip-path="url(#shoesClip)" />
  </g>

  <g filter="url(#shadow)">
    <rect x="36" y="40" width="260" height="310" rx="28" fill="rgba(255,250,243,0.92)" />
    <text x="62" y="90" font-family="Georgia, serif" font-size="34" fill="#1f2a2e">Try-On Preview</text>
    <text x="62" y="130" font-family="Avenir Next, Arial, sans-serif" font-size="18" fill="#6e6a63">Provider: mock_svg</text>
    <text x="62" y="170" font-family="Avenir Next, Arial, sans-serif" font-size="18" fill="#6e6a63">Top: {escape(outfit.top_item.brand or "Closet item")}</text>
    <text x="62" y="202" font-family="Avenir Next, Arial, sans-serif" font-size="18" fill="#6e6a63">Pants: {escape(outfit.pants_item.brand or "Closet item")}</text>
    <text x="62" y="234" font-family="Avenir Next, Arial, sans-serif" font-size="18" fill="#6e6a63">Shoes: {escape(outfit.shoes_item.brand or "Closet item")}</text>
    <text x="62" y="282" font-family="Avenir Next, Arial, sans-serif" font-size="16" fill="#1f2a2e">This is a styled preview overlay,</text>
    <text x="62" y="306" font-family="Avenir Next, Arial, sans-serif" font-size="16" fill="#1f2a2e">not a photorealistic garment simulation.</text>
  </g>

  <g filter="url(#shadow)">
    <rect x="540" y="950" width="320" height="180" rx="28" fill="rgba(255,250,243,0.94)" />
    <text x="570" y="998" font-family="Georgia, serif" font-size="24" fill="#1f2a2e">Why this look</text>
    <foreignObject x="570" y="1018" width="260" height="92">
      <div xmlns="http://www.w3.org/1999/xhtml" style="font-family: Avenir Next, Arial, sans-serif; font-size: 16px; line-height: 1.45; color: #4b5560;">
        {reason}
      </div>
    </foreignObject>
  </g>
</svg>
"""


def _save_svg(svg_content: str) -> str:
    TRY_ON_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}.svg"
    file_path = TRY_ON_UPLOAD_DIR / filename
    file_path.write_text(svg_content, encoding="utf-8")
    return f"uploads/try_on_previews/{filename}"


def _get_hydrated_outfit(db: Session, outfit_id: int) -> OutfitRecommendation | None:
    return db.scalar(
        select(OutfitRecommendation)
        .where(OutfitRecommendation.id == outfit_id)
        .options(
            joinedload(OutfitRecommendation.request),
            joinedload(OutfitRecommendation.top_item),
            joinedload(OutfitRecommendation.pants_item),
            joinedload(OutfitRecommendation.shoes_item),
            selectinload(OutfitRecommendation.try_on_previews),
        )
    )


def generate_try_on_preview(db: Session, user_id: int, outfit_id: int) -> TryOnPreview:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    profile = db.scalar(select(UserProfile).where(UserProfile.user_id == user_id))
    if not profile or not profile.full_body_image_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A full-body profile image is required before generating a try-on preview.",
        )

    outfit = _get_hydrated_outfit(db, outfit_id)
    if not outfit or outfit.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit recommendation not found.")

    if VIRTUAL_TRY_ON_PROVIDER != "mock_svg":
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"Virtual try-on provider '{VIRTUAL_TRY_ON_PROVIDER}' is not implemented in this local setup.",
        )

    svg_content = _render_mock_svg_preview(profile.full_body_image_path, outfit)
    preview_path = _save_svg(svg_content)
    preview = TryOnPreview(
        user_id=user_id,
        outfit_id=outfit_id,
        provider=VIRTUAL_TRY_ON_PROVIDER,
        preview_image_path=preview_path,
    )
    db.add(preview)
    db.commit()
    db.refresh(preview)
    return preview


def list_try_on_previews(db: Session, user_id: int) -> list[TryOnPreview]:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return list(
        db.scalars(
            select(TryOnPreview)
            .where(TryOnPreview.user_id == user_id)
            .order_by(TryOnPreview.created_at.desc())
        )
    )
