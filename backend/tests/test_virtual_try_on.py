import tempfile
import unittest
from base64 import b64decode
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.clothing import ClothingItem
from app.models.profile import UserProfile
from app.models.recommendation import OutfitRecommendation, RecommendationRequest
from app.models.user import User
from app.services import virtual_try_on as virtual_try_on_module


PNG_PIXEL = b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9WlAb6UAAAAASUVORK5CYII="
)


class VirtualTryOnTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(self.temp_dir.name) / "try_on.db"
        self.engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.SessionLocal()

    def tearDown(self) -> None:
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()
        self.temp_dir.cleanup()

    def test_generate_try_on_preview_creates_svg_file_and_record(self) -> None:
        user = User(name="Preview Tester", email="preview@example.com")
        self.db.add(user)
        self.db.flush()

        profile = UserProfile(
            user_id=user.id,
            full_body_image_path="uploads/profile_images/person.png",
            style_preferences=["clean"],
            body_goals=["look taller"],
            color_preferences=["white"],
            avoid_tags=[],
            notes="try on test",
        )
        self.db.add(profile)

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
            extra_note=None,
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
            total_score=88.0,
            compatibility_score=86.0,
            user_fit_score=84.0,
            style_match_score=91.0,
            scene_match_score=82.0,
            weather_match_score=80.0,
            preference_score=75.0,
            repetition_penalty=5.0,
            reason_text="Test explanation",
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(outfit)
        self.db.commit()

        uploads_root = Path(self.temp_dir.name) / "uploads"
        (uploads_root / "profile_images").mkdir(parents=True, exist_ok=True)
        (uploads_root / "clothing_items").mkdir(parents=True, exist_ok=True)
        (uploads_root / "profile_images" / "person.png").write_bytes(PNG_PIXEL)
        (uploads_root / "clothing_items" / "top.png").write_bytes(PNG_PIXEL)
        (uploads_root / "clothing_items" / "pants.png").write_bytes(PNG_PIXEL)
        (uploads_root / "clothing_items" / "shoes.png").write_bytes(PNG_PIXEL)

        preview_dir = Path(self.temp_dir.name) / "uploads" / "try_on_previews"
        with patch.object(virtual_try_on_module, "TRY_ON_UPLOAD_DIR", preview_dir), patch.object(
            virtual_try_on_module, "VIRTUAL_TRY_ON_PROVIDER", "mock_svg"
        ), patch.object(virtual_try_on_module, "UPLOAD_DIR", uploads_root):
            preview = virtual_try_on_module.generate_try_on_preview(self.db, user.id, outfit.id)

        self.assertEqual(preview.provider, "mock_svg")
        self.assertTrue(preview.preview_image_path.endswith(".svg"))
        file_path = Path(self.temp_dir.name) / preview.preview_image_path
        self.assertTrue(file_path.exists())
        self.assertIn("Try-On Preview", file_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
