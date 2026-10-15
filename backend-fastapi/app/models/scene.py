from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._time import utcnow


class Scene(Base):
    __tablename__ = "scenes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id"),
        index=True
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    user_role: Mapped[str] = mapped_column(String(100))
    goal: Mapped[str] = mapped_column(Text)
    ai_roles: Mapped[list] = mapped_column(JSON)
    conflict: Mapped[str] = mapped_column(Text)
    task_chain: Mapped[list] = mapped_column(JSON)
    language_goals: Mapped[str] = mapped_column(Text)
    final_output: Mapped[str] = mapped_column(Text)
    difficulty: Mapped[str] = mapped_column(
        String(20),
        default="standard"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utcnow
    )

    article = relationship(
        "Article",
        back_populates="scenes"
    )
