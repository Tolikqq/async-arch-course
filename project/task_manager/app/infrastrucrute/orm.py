import enum
import uuid

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from app.database import Base
from app.domain.task import Task, StatusEnum
from app.domain.worker import Worker, Role


class RoleEnum(enum.StrEnum):
    admin = "admin"
    analytics = "analytics"
    worker = "worker"
    accounting = "accounting"
    manager = "manager"


ASSIGNABLE_ROLES = {RoleEnum.analytics.value, RoleEnum.worker.value, RoleEnum.accounting.value}


class WorkerORM(Base):
    __tablename__ = "workers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    email: Mapped[str]
    role: Mapped[RoleEnum]

    @classmethod
    def from_domain(cls, worker: Worker) -> "WorkerORM":
        return WorkerORM(
            id=worker.id,
            email=worker.email,
            role=RoleEnum(worker.role),
        )

    def to_domain(self) -> Worker:
        return Worker(id=self.id, email=self.email, role=Role(self.role))


class TaskORM(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    description: Mapped[str]
    status: Mapped[StatusEnum]
    assignee_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workers.id"), nullable=True)
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workers.id"), nullable=True)

    @classmethod
    def from_domain(cls, task: Task) -> "TaskORM":
        return TaskORM(
            id=task.id,
            description=task.description,
            status=task.status,
            assignee_id=task.assignee_id,
            creator_id=task.creator_id
        )

    def to_domain(self) -> Task:
        return Task(
            id=self.id,
            description=self.description,
            status=self.status,
            assignee_id=self.assignee_id,
            creator_id=self.creator_id
        )
