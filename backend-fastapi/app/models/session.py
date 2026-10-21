from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._time import utcnow


class Session(Base):
    __tablename__ = "sessions"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), index=True, nullable=False)
    scene_id: Mapped[int] = mapped_column(ForeignKey("scenes.id"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)
    
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
