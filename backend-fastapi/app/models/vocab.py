from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models._time import utcnow


class Vocab(Base):
    __tablename__ = "vocabs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)

    word: Mapped[str] = mapped_column(String(100), index=True)
    meaning: Mapped[str] = mapped_column(String(255))
    example: Mapped[str] = mapped_column(Text, default="")
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    mastered: Mapped[int] = mapped_column(Integer, default=0)  # 0 未掌握 / 1 已掌握

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)