from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models._time import utcnow


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.id"), unique=True, index=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    grammar_issues: Mapped[list] = mapped_column(JSON, default=list)
    vocab_suggestions: Mapped[list] = mapped_column(JSON, default=list)
    expression_upgrades: Mapped[list] = mapped_column(JSON, default=list)
    task_completion: Mapped[dict] = mapped_column(JSON, default=dict)
    overall_score: Mapped[int] = mapped_column(default=0)
    summary: Mapped[str] = mapped_column(String(500), default="")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)