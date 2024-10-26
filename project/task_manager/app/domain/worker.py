
from dataclasses import dataclass
from enum import StrEnum

from app.common.domain.entities import AggregateRoot
from uuid import UUID


class Role(StrEnum):
    MANAGER = 'manager'
    ADMIN = 'admin'
    WORKER = 'worker'
    ACCOUNTANT = 'accountant'


ADMIN_ROLES = {Role.ADMIN.value, Role.MANAGER.value}


@dataclass
class Worker(AggregateRoot):
    id: UUID
    email: str
    role: Role

    @classmethod
    def new(cls, id: UUID, email: str, role: Role) -> "Worker":
        return Worker(
            id=id,
            email=email,
            role=Role(role),
        )

    @property
    def is_admin_role(self) -> bool:
        return self.role in ADMIN_ROLES
