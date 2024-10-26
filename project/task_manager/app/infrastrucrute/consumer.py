import asyncio
from typing import Any

from aiokafka import AIOKafkaConsumer, ConsumerRecord
from schema_registry.client import AsyncSchemaRegistryClient
from schema_registry.serializers import AsyncAvroMessageSerializer  # type: ignore[attr-defined]
from aiokafka.consumer.fetcher import OffsetResetStrategy
from loguru import logger
from app.infrastrucrute.di.container import DIContainer
from settings.config import get_settings, AppSettings


class KafkaAVROConsumer:
    def __init__(self, consumer: AIOKafkaConsumer, schema_registry_url: str) -> None:
        self.consumer = consumer
        self.schema_registry_client = AsyncSchemaRegistryClient(
            url=schema_registry_url,
        )
        self.serializer = AsyncAvroMessageSerializer(self.schema_registry_client)

    async def start(self) -> None:
        await self.consumer.start()

    async def stop(self) -> None:
        await self.consumer.stop()

    async def get_event(self) -> ConsumerRecord:
        return await self.consume()

    async def consumer_commit(self) -> None:
        await self.consumer.commit()

    async def consume(self) -> ConsumerRecord:
        return await self.consumer.getone()

    async def decode_record(self, record: bytes) -> dict[str, Any] | None:
        return await self.serializer.decode_message(record)


class BaseHandler:
    async def execute(self, record: dict[str, Any]) -> None:
        pass


class KafkaConsumerApp:
    def __init__(self, app_settings: AppSettings) -> None:
        self.settings = app_settings
        self.kafka_consumer: KafkaAVROConsumer
        self.container = self.create_di_container()
        self._handler_by_topic: dict[str, BaseHandler] = {}

    def create_consumer(self) -> KafkaAVROConsumer:
        topics = [
            "auth.user-stream",
        ]
        return KafkaAVROConsumer(
            consumer=AIOKafkaConsumer(
                *topics,
                group_id="task_manager",
                bootstrap_servers='localhost:9092',
                auto_offset_reset=OffsetResetStrategy.to_str(OffsetResetStrategy.EARLIEST),
                enable_auto_commit=False,
            ),
            schema_registry_url=self.settings.SCHEMA_REGISTRY_URL
        )

    def create_di_container(self) -> DIContainer:
        container = DIContainer()
        container.wire(packages=["app", __name__])
        return container

    async def run(self) -> None:
        await self.startup()
        try:
            await self.run_event_handler()
        finally:
            await self.shutdown()

    async def startup(self) -> None:
        await self.startup_di_resources()
        self.kafka_consumer = self.create_consumer()
        await self.kafka_consumer.start()

    async def shutdown(self) -> None:
        shutdown_coro = self.container.shutdown_resources()
        if shutdown_coro:
            await shutdown_coro
        await self.kafka_consumer.stop()

    async def run_event_handler(self) -> None:
        while True:
            try:
                record = await self.kafka_consumer.get_event()
                await self._process_event(record=record)
            except Exception as error:
                print("error in kafka consumer")
                logger.exception("got unhandled exception", error=repr(error))

    async def _process_event(self, record: ConsumerRecord) -> None:
        handler = await self._get_handler(topic=record.topic)

        event_data = await self.kafka_consumer.decode_record(record.value)
        if event_data is None:
            raise ValueError(f"topic {record.topic}: record is empty")

        await handler.execute(record=event_data)
        await self.kafka_consumer.consumer_commit()

    async def startup_di_resources(self) -> None:
        await self.container.init_resources()  # type: ignore[misc]

    async def _get_handler(self, topic: str) -> BaseHandler:  # noqa: PLR0912
        if handler_by_topic := self._handler_by_topic.get(topic):
            return handler_by_topic

        handler: BaseHandler
        match topic:
            case "auth.user-stream":
                handler = self.container.kafka_handlers.account_changes_event_handler()
            case _:
                raise ValueError(f"Unknown kafka topic: {topic}")

        self._handler_by_topic[topic] = handler
        return handler


if __name__ == "__main__":
    settings = get_settings()
    consumer = KafkaConsumerApp(app_settings=settings)

    asyncio.run(consumer.run())


