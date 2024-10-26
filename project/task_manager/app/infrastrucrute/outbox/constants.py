from enum import StrEnum


class OutboxEventTypes(StrEnum):
    task_assigned = "task_assigned"


NOTIFICATIONS_OUTBOX_LIMIT = 100
