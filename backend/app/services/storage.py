from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status


ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def save_upload_file(upload: UploadFile, destination_dir: Path, relative_prefix: str) -> str:
    if not upload.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing upload filename.")

    suffix = Path(upload.filename).suffix.lower()
    if suffix not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only jpg, jpeg, png, and webp uploads are supported.",
        )

    destination_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{suffix}"
    file_path = destination_dir / filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)

    return f"{relative_prefix}/{filename}"


def remove_file(relative_path: str | None, root_dir: Path) -> None:
    if not relative_path:
        return

    file_path = root_dir / relative_path.replace("uploads/", "")
    if file_path.exists() and file_path.is_file():
        file_path.unlink()
