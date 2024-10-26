from dataclasses import dataclass
from schema_registry.client import AsyncSchemaRegistryClient
from schema_registry.serializers import AsyncAvroMessageSerializer  # type: ignore[attr-defined]

from app.infrastrucrute.kafka.adapters.base import KafkaAdapter
from app.infrastrucrute.kafka.client import KafkaClient, KafkaTopicsEnum
from app.infrastrucrute.kafka.encoder.avro import KafkaAvroEncoder
from settings.config import AppSettings


@dataclass
class KafkaAvroAdapter(KafkaAdapter):
    client: KafkaClient
    encoder: KafkaAvroEncoder


def create_kafka_avro_adapter(
        client: KafkaClient,
        settings: AppSettings,
) -> KafkaAvroAdapter:
    topic_to_value_subject_map = {
        KafkaTopicsEnum.user_stream.value: KafkaTopicsEnum.user_stream.get_schema_name(),
        KafkaTopicsEnum.task_assigned.value: KafkaTopicsEnum.task_assigned.get_schema_name(),
        KafkaTopicsEnum.task_completed.value: KafkaTopicsEnum.task_completed.get_schema_name(),
            }
    return KafkaAvroAdapter(
        client=client,
        encoder=KafkaAvroEncoder(
            schema_registry_client=AsyncSchemaRegistryClient(url=settings.SCHEMA_REGISTRY_URL),
            topic_to_value_subject_map=topic_to_value_subject_map,
            serializer=AsyncAvroMessageSerializer(AsyncSchemaRegistryClient(url=settings.SCHEMA_REGISTRY_URL)),
        ),
    )
