from dataclasses import dataclass
from typing import Any

from app.ctx_vars import get_ctx_request_id
from app.infrastrucrute.kafka.client import KafkaClient
from app.infrastrucrute.kafka.encoder.base import KafkaEncoder


@dataclass
class KafkaAdapter:
    client: KafkaClient
    encoder: KafkaEncoder

    async def send(
            self,
            topic: str,
            record: dict[str, Any],
            key: dict[str, int] | None = None,
            headers: dict[str, Any] | None = None,
    ) -> None:
        headers = self._add_request_headers(headers=headers)

        await self.client.send(
            topic,
            record=await self.encoder.encode_message(record, topic),
            key=await self.encoder.encode_key(key, topic),
            headers=await self.encoder.encode_headers(headers),
        )

    @staticmethod
    def _add_request_headers(headers: dict[Any, Any] | None = None) -> dict[str, Any] | None:
        headers = headers or {}
        if request_id := get_ctx_request_id():
            headers["request_id"] = request_id

        return headers if headers else None