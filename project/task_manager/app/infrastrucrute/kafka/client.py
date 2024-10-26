from enum import StrEnum
from typing import Iterable
from aiokafka import AIOKafkaProducer
from settings.config import AppSettings


class KafkaTopicsEnum(StrEnum):
    user_stream = "auth.user-stream"
    task_assigned = "task-manager.task-assigned"
    task_completed = "task-manager.task-completed"

    def get_schema_name(self) -> str:
        return self.value + "-value"


class KafkaClient:
    def __init__(self, producer: AIOKafkaProducer) -> None:
        self.producer = producer

    async def start(self) -> None:
        await self.producer.start()

    async def stop(self) -> None:
        await self.producer.stop()

    async def send(
        self,
        topic: str,
        record: bytes,
        key: bytes | None = None,
        headers: Iterable[tuple[str, bytes]] | None = None,
        timestamp_ms: int | None = None,
    ) -> None:
        if timestamp_ms:
            await self.producer.send(topic, value=record, key=key, timestamp_ms=timestamp_ms, headers=headers)
        else:
            await self.producer.send_and_wait(topic, value=record, key=key, headers=headers)


def create_kafka_client(settings: AppSettings) -> KafkaClient:
    return KafkaClient(producer=AIOKafkaProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS))