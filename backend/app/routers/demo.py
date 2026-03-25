from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.clothing import ClothingItem
from app.schemas.demo import DemoSeedResponse
from app.services.demo_seed import seed_demo_user
from app.database import get_db


router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/seed", response_model=DemoSeedResponse)
def create_demo_seed(db: Session = Depends(get_db)) -> DemoSeedResponse:
    user, created = seed_demo_user(db)
    clothing_count = len(list(db.scalars(select(ClothingItem).where(ClothingItem.user_id == user.id))))
    message = "Demo closet created." if created else "Existing demo closet loaded."
    return DemoSeedResponse(
        user=user,
        created=created,
        clothing_count=clothing_count,
        message=message,
    )
