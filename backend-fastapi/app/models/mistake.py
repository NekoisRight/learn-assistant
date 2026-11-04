from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models._time import utcnow


class Mistake(Base):
    __tablename__ = "mistakes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)

    original: Mapped[str] = mapped_column(Text)
    corrected: Mapped[str] = mapped_column(Text)
    reason: Mapped[str] = mapped_column(String(500))
    category: Mapped[str] = mapped_column(String(50), default="grammar")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)