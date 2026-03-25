from app.schemas.common import ORMModel
from app.schemas.user import UserRead


class DemoSeedResponse(ORMModel):
    user: UserRead
    created: bool
    clothing_count: int
    message: str
