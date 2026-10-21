from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)

class MessageOut(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class SendMessageResponse(BaseModel):
    user_message: MessageOut
    ai_message: MessageOut
