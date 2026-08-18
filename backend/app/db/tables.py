from datetime import datetime, timezone

from sqlalchemy import DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class StoredProfile(Base):
    __tablename__ = "profiles"

    id: Mapped[str] = mapped_column(primary_key=True)
    profile_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class StoredRun(Base):
    __tablename__ = "runs"

    id: Mapped[str] = mapped_column(primary_key=True)
    profile_id: Mapped[str | None] = mapped_column(nullable=True)
    response_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

