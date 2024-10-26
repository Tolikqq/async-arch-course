from dataclasses import dataclass
from typing import Any

from settings.kafka.client import KafkaClient
from settings.kafka.encoder.base import KafkaEncoder


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
        await self.client.send(
            topic,
            record=await self.encoder.encode_message(record, topic),
            key=await self.encoder.encode_key(key, topic),
            headers=await self.encoder.encode_headers(headers),
        )
