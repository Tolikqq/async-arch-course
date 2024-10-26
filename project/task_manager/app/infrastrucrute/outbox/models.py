from datetime import datetime

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Outbox(Base):
    __tablename__ = "outbox"

    id: Mapped[int] = mapped_column("id", autoincrement=True, primary_key=True)
    event_type: Mapped[str] = mapped_column("event_type", String(64), nullable=False)
    payload: Mapped[str] = mapped_column("payload", nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        "occurred_at", default=func.now(), nullable=False
    )
    processed_at: Mapped[datetime | None] = mapped_column("processed_at", nullable=True)