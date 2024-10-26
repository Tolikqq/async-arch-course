from typing import AsyncGenerator

from dependency_injector import containers, providers
from dependency_injector.providers import Singleton, Resource, Callable

from app.database import Database
from app.infrastructure.dispatcher import UserEventDispatcher
from settings.config import AppSettings
from settings.kafka.adapters.avro import create_kafka_avro_adapter
from settings.kafka.client import create_kafka_client, KafkaClient, KafkaTopicsEnum


async def initialize_kafka_client(kafka_client: KafkaClient) -> AsyncGenerator[KafkaClient, None]:
    await kafka_client.start()
    yield kafka_client
    await kafka_client.stop()


class AdaptersContainer(containers.DeclarativeContainer):
    settings: providers.Dependency[AppSettings] = providers.Dependency()

    database = Singleton(
        Database,
        url=settings.provided.DATABASE_URL,
        debug=settings.provided.DEBUG,
    )

    kafka_client_ = Singleton(create_kafka_client, settings=settings)
    kafka_client = Resource(initialize_kafka_client, kafka_client_, )
    kafka_avro_adapter = Singleton(
        create_kafka_avro_adapter,
        client=kafka_client,
        settings=settings,
    )

    user_event_dispatcher = Singleton(
        UserEventDispatcher,
        producer=kafka_avro_adapter
    )
