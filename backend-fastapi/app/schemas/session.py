from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.scene import SceneOut


class SessionCreate(BaseModel):
    article_id: int
    scene_id: int


class SessionOut(BaseModel):
    id: int
    user_id: int
    article_id: int
    scene_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SessionDetail(BaseModel):
    id: int
    user_id: int
    article_id: int
    scene_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    scene: SceneOut | None = None

    model_config = ConfigDict(from_attributes=True)
