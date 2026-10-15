from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._time import utcnow


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    level: Mapped[str] = mapped_column(String(20), default="B1")
    source: Mapped[str] = mapped_column(String(200), default="user_upload")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    scenes = relationship(
        "Scene",
        back_populates="article",
        cascade="all, delete-orphan"
    )
