from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BACKEND_DIR / "uploads"
PROFILE_UPLOAD_DIR = UPLOAD_DIR / "profile_images"
CLOTHING_UPLOAD_DIR = UPLOAD_DIR / "clothing_items"
DATABASE_URL = f"sqlite:///{BACKEND_DIR / 'wardrobe_ai.db'}"

