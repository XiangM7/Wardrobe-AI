from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.try_on import TryOnPreviewRead
from app.services.virtual_try_on import generate_try_on_preview, list_try_on_previews


router = APIRouter(prefix="/try-on", tags=["try-on"])


@router.get("/{user_id}", response_model=list[TryOnPreviewRead])
def get_try_on_previews(user_id: int, db: Session = Depends(get_db)) -> list[TryOnPreviewRead]:
    return list_try_on_previews(db=db, user_id=user_id)


@router.post("/{user_id}/{outfit_id}", response_model=TryOnPreviewRead, status_code=status.HTTP_201_CREATED)
def create_try_on_preview(user_id: int, outfit_id: int, db: Session = Depends(get_db)) -> TryOnPreviewRead:
    return generate_try_on_preview(db=db, user_id=user_id, outfit_id=outfit_id)
