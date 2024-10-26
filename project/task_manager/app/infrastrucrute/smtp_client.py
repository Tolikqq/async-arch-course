from dataclasses import dataclass
from email.message import EmailMessage

import aiosmtplib

DEFAULT_EMAIL_FROM = "root@localhost"


@dataclass(slots=True)
class SMTPMessage:
    subject: str
    content: str
    email_to: str
    email_from: str


class SMTPClient:
    def __init__(
        self,
        *,
        hostname: str,
        port: int,
    ) -> None:
        self._smtp = aiosmtplib.SMTP(hostname=hostname, port=port)

    async def send_message(self, message: SMTPMessage) -> None:
        email_message = self._prepare_message(message)
        await self._send_message(email_message)

    async def _send_message(self, email_message: EmailMessage) -> None:
        print(f"send email {email_message}")
        # async with self._smtp as session:
        #     await session.send_message(email_message)

    def _prepare_message(self, message: SMTPMessage) -> EmailMessage:
        email_message = EmailMessage()
        email_message["From"] = message.email_from
        email_message["To"] = message.email_to
        email_message["Subject"] = message.subject
        email_message.set_content(message.content)
        return email_message