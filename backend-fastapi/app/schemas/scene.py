from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AIRole(BaseModel):
    name: str
    stance: str
    example: str

class TaskStep(BaseModel):
    stage: str
    task: str
    user_action: str

class SceneCard(BaseModel):

    title: str
    user_role: str
    goal: str
    ai_roles: list[AIRole]
    conflict: str
    task_chain: list[TaskStep]
    language_goals: str
    final_output: str
    difficulty: str = "standard"

class SceneGenerateRequest(BaseModel):
    article_id: int
    difficulty: str = Field(default="standard", max_length=20)
    extra_instructions: str | None = None

class SceneOut(BaseModel):
    id: int
    article_id: int
    title: str
    user_role: str
    goal: str
    ai_roles: list[AIRole]
    conflict: str
    task_chain: list[TaskStep]
    language_goals: str
    final_output: str
    difficulty: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
