from datetime import datetime

from app.schemas.common import ORMModel


class TryOnPreviewRead(ORMModel):
    id: int
    user_id: int
    outfit_id: int
    provider: str
    preview_image_path: str
    created_at: datetime
