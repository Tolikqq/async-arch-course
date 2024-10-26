from dataclasses import dataclass
from schema_registry.client import AsyncSchemaRegistryClient
from schema_registry.serializers import AsyncAvroMessageSerializer

from settings.config import AppSettings
from settings.kafka.adapters.base import KafkaAdapter
from settings.kafka.client import KafkaClient, KafkaTopicsEnum
from settings.kafka.encoder.avro import KafkaAvroEncoder


@dataclass
class KafkaAvroAdapter(KafkaAdapter):
    client: KafkaClient
    encoder: KafkaAvroEncoder


def create_kafka_avro_adapter(
        client: KafkaClient,
        settings: AppSettings,
) -> KafkaAvroAdapter:
    topic_to_value_subject_map = {
                KafkaTopicsEnum.user_stream.value: KafkaTopicsEnum.user_stream.get_schema_name()
            }
    return KafkaAvroAdapter(
        client=client,
        encoder=KafkaAvroEncoder(
            schema_registry_client=AsyncSchemaRegistryClient(url=settings.SCHEMA_REGISTRY_URL),
            topic_to_value_subject_map=topic_to_value_subject_map,
            serializer=AsyncAvroMessageSerializer(AsyncSchemaRegistryClient(url=settings.SCHEMA_REGISTRY_URL)),
        ),
    )
