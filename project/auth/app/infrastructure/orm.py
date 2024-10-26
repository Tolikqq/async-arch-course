import enum
import uuid
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class RoleEnum(str, enum.Enum):
    admin = "admin"
    analytics = "analytics"
    worker = "worker"
    accounting = "accounting"


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    public_id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, unique=True)
    password_hash: Mapped[str]

    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), )
    role: Mapped[RoleEnum]
