from dataclasses import dataclass
from uuid import UUID

from app.infrastrucrute.smtp_client import SMTPClient, SMTPMessage, DEFAULT_EMAIL_FROM


@dataclass
class EmailNotificationGateway:
    smtp_adapter: SMTPClient

    async def send_assigned_task(self, task_id: UUID, worker_email: str) -> None:
        message = self._build_notification_message(task_id=task_id, worker_email=worker_email)
        await self.smtp_adapter.send_message(message)

    def _build_notification_message(self, task_id: UUID, worker_email: str) -> SMTPMessage:
        return SMTPMessage(
            subject="New task",
            content=f"You was assigned for new task {task_id}",
            email_to=worker_email,
            email_from=DEFAULT_EMAIL_FROM
        )
