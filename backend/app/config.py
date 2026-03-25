import os
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BACKEND_DIR / "uploads"
PROFILE_UPLOAD_DIR = UPLOAD_DIR / "profile_images"
CLOTHING_UPLOAD_DIR = UPLOAD_DIR / "clothing_items"
TRY_ON_UPLOAD_DIR = UPLOAD_DIR / "try_on_previews"
DATABASE_URL = f"sqlite:///{BACKEND_DIR / 'wardrobe_ai.db'}"
VIRTUAL_TRY_ON_PROVIDER = os.getenv("VIRTUAL_TRY_ON_PROVIDER", "mock_svg")
