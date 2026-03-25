import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.clothing import ClothingItem
from app.models.profile import UserProfile
from app.models.user import User
from app.services import demo_seed as demo_seed_module


class DemoSeedTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(self.temp_dir.name) / "seed.db"
        self.engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.SessionLocal()

    def tearDown(self) -> None:
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()
        self.temp_dir.cleanup()

    def test_seed_demo_user_is_idempotent(self) -> None:
        uploads_root = Path(self.temp_dir.name) / "uploads"
        clothing_dir = uploads_root / "clothing_items"
        profile_dir = uploads_root / "profile_images"

        with patch.object(demo_seed_module, "CLOTHING_UPLOAD_DIR", clothing_dir), patch.object(
            demo_seed_module, "PROFILE_UPLOAD_DIR", profile_dir
        ):
            user, created = demo_seed_module.seed_demo_user(self.db)
            self.assertTrue(created)
            self.assertEqual(user.email, demo_seed_module.DEMO_EMAIL)

            users = list(self.db.scalars(select(User)))
            profiles = list(self.db.scalars(select(UserProfile)))
            clothing_items = list(self.db.scalars(select(ClothingItem)))
            self.assertEqual(len(users), 1)
            self.assertEqual(len(profiles), 1)
            self.assertEqual(len(clothing_items), 8)

            again_user, created_again = demo_seed_module.seed_demo_user(self.db)
            self.assertFalse(created_again)
            self.assertEqual(user.id, again_user.id)
            self.assertEqual(len(list(self.db.scalars(select(ClothingItem)))), 8)


if __name__ == "__main__":
    unittest.main()
