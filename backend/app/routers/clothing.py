from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import CLOTHING_UPLOAD_DIR, UPLOAD_DIR
from app.database import get_db
from app.models.clothing import ClothingItem
from app.models.user import User
from app.schemas.clothing import ClothingItemRead, ClothingItemUpdate
from app.services.storage import remove_file, save_upload_file


router = APIRouter(prefix="/clothing", tags=["clothing"])
ALLOWED_CATEGORIES = {"tops", "pants", "shoes"}


def parse_csv_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def normalize_category(category: str) -> str:
    normalized = category.strip().lower()
    if normalized not in ALLOWED_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category must be one of: tops, pants, shoes.",
        )
    return normalized


def parse_date_value(raw_value: str | None) -> date | None:
    if not raw_value:
        return None
    try:
        return date.fromisoformat(raw_value)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid last_worn_date.") from exc


@router.post("/{user_id}", response_model=ClothingItemRead, status_code=status.HTTP_201_CREATED)
def create_clothing_item(
    user_id: int,
    image: UploadFile = File(...),
    category: str = Form(...),
    primary_color: str | None = Form(None),
    secondary_color: str | None = Form(None),
    style_tags: str | None = Form(None),
    season_tags: str | None = Form(None),
    formality: str | None = Form(None),
    fit: str | None = Form(None),
    brand: str | None = Form(None),
    is_favorite: bool = Form(False),
    last_worn_date: str | None = Form(None),
    db: Session = Depends(get_db),
) -> ClothingItem:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    image_path = save_upload_file(image, CLOTHING_UPLOAD_DIR, "uploads/clothing_items")
    clothing_item = ClothingItem(
        user_id=user_id,
        image_path=image_path,
        category=normalize_category(category),
        primary_color=(primary_color or "").strip() or None,
        secondary_color=(secondary_color or "").strip() or None,
        style_tags=parse_csv_list(style_tags),
        season_tags=parse_csv_list(season_tags),
        formality=(formality or "").strip() or None,
        fit=(fit or "").strip() or None,
        brand=(brand or "").strip() or None,
        is_favorite=is_favorite,
        last_worn_date=parse_date_value(last_worn_date),
    )
    db.add(clothing_item)
    db.commit()
    db.refresh(clothing_item)
    return clothing_item


@router.get("/{user_id}", response_model=list[ClothingItemRead])
def get_clothing_items(user_id: int, db: Session = Depends(get_db)) -> list[ClothingItem]:
    return list(
        db.scalars(
            select(ClothingItem)
            .where(ClothingItem.user_id == user_id)
            .order_by(ClothingItem.is_favorite.desc(), ClothingItem.created_at.desc())
        )
    )


@router.put("/item/{item_id}", response_model=ClothingItemRead)
def update_clothing_item(
    item_id: int,
    payload: ClothingItemUpdate,
    db: Session = Depends(get_db),
) -> ClothingItem:
    clothing_item = db.get(ClothingItem, item_id)
    if not clothing_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clothing item not found.")

    updates = payload.model_dump(exclude_unset=True)
    if "category" in updates and updates["category"] is not None:
        updates["category"] = normalize_category(updates["category"])

    for field_name, value in updates.items():
        setattr(clothing_item, field_name, value)

    db.commit()
    db.refresh(clothing_item)
    return clothing_item


@router.delete("/item/{item_id}", status_code=status.HTTP_200_OK)
def delete_clothing_item(item_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    clothing_item = db.get(ClothingItem, item_id)
    if not clothing_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clothing item not found.")

    remove_file(clothing_item.image_path, UPLOAD_DIR)
    db.delete(clothing_item)
    db.commit()
    return {"detail": "Clothing item deleted."}
