from typing import AsyncGenerator

from dependency_injector import containers, providers
from dependency_injector.providers import Singleton, Resource

from app.database import Database
from app.infrastrucrute.kafka.adapters.avro import create_kafka_avro_adapter
from app.infrastrucrute.kafka.client import create_kafka_client, KafkaClient
from app.infrastrucrute.smtp_client import SMTPClient
from settings.config import AppSettings


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

    smtp_adapter: Singleton[SMTPClient] = Singleton(
        SMTPClient,
        hostname=settings.provided.SMTP_HOSTNAME,
        port=settings.provided.SMTP_PORT,
    )
