import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.clothing import ClothingItem
from app.models.feedback import UserFeedback
from app.models.recommendation import OutfitRecommendation, RecommendationRequest
from app.models.user import User
from app.schemas.feedback import FeedbackCreate
from app.services.feedback_service import save_feedback


class FeedbackServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(self.temp_dir.name) / "test.db"
        self.engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.SessionLocal()

    def tearDown(self) -> None:
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()
        self.temp_dir.cleanup()

    def test_save_feedback_marks_outfit_items_as_worn(self) -> None:
        user = User(name="Tester", email="tester@example.com")
        self.db.add(user)
        self.db.flush()

        top = ClothingItem(
            user_id=user.id,
            image_path="uploads/clothing_items/top.png",
            category="tops",
            primary_color="white",
            style_tags=["clean"],
            season_tags=["spring"],
            formality="casual",
            fit="regular",
            brand="Top",
        )
        pants = ClothingItem(
            user_id=user.id,
            image_path="uploads/clothing_items/pants.png",
            category="pants",
            primary_color="navy",
            style_tags=["clean"],
            season_tags=["spring"],
            formality="casual",
            fit="regular",
            brand="Pants",
        )
        shoes = ClothingItem(
            user_id=user.id,
            image_path="uploads/clothing_items/shoes.png",
            category="shoes",
            primary_color="navy",
            style_tags=["clean"],
            season_tags=["spring"],
            formality="casual",
            fit="regular",
            brand="Shoes",
        )
        self.db.add_all([top, pants, shoes])
        self.db.flush()

        request = RecommendationRequest(
            user_id=user.id,
            target_style="clean",
            target_scene="school",
            weather="mild",
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(request)
        self.db.flush()

        outfit = OutfitRecommendation(
            request_id=request.id,
            user_id=user.id,
            top_item_id=top.id,
            pants_item_id=pants.id,
            shoes_item_id=shoes.id,
            total_score=90.0,
            compatibility_score=90.0,
            user_fit_score=88.0,
            style_match_score=92.0,
            scene_match_score=87.0,
            weather_match_score=85.0,
            preference_score=80.0,
            repetition_penalty=0.0,
            reason_text="Test outfit",
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(outfit)
        self.db.commit()

        payload = FeedbackCreate(
            outfit_id=outfit.id,
            liked=True,
            saved=True,
            worn=True,
            feedback_text="Worked well today.",
        )
        feedback = save_feedback(db=self.db, user_id=user.id, payload=payload)

        self.db.refresh(top)
        self.db.refresh(pants)
        self.db.refresh(shoes)
        self.assertEqual(feedback.worn, True)
        self.assertEqual(top.last_worn_date, date.today())
        self.assertEqual(pants.last_worn_date, date.today())
        self.assertEqual(shoes.last_worn_date, date.today())

        updated_feedback = save_feedback(
            db=self.db,
            user_id=user.id,
            payload=FeedbackCreate(
                outfit_id=outfit.id,
                liked=False,
                saved=False,
                worn=True,
                feedback_text="Updating feedback",
            ),
        )
        feedback_rows = list(self.db.scalars(select(UserFeedback)))
        self.assertEqual(len(feedback_rows), 1) 
        self.assertEqual(updated_feedback.feedback_text, "Updating feedback")


if __name__ == "__main__":
    unittest.main()
