import uuid
from dataclasses import dataclass
from typing import Any

from dataclasses_avroschema import AvroModel
from kafka import KafkaAdminClient, KafkaProducer
from kafka.admin import NewTopic
from schema_registry.client import SchemaRegistryClient
from schema_registry.client.schema import AvroSchema
from schema_registry.client.utils import VALID_LEVELS
from schema_registry.serializers import AvroMessageSerializer

from infrastructure.avro_models import UserCreatedEvent


@dataclass
class Config:
    kafka_bootstrap_servers: str
    schema_registry_url: str


class KafkaAvroTopicHelper:
    """For local use only"""

    def __init__(self, topic_name: str, subject: str, config: Config) -> None:
        self.topic_name = topic_name
        self.subject = subject
        self.kafka_admin_client = KafkaAdminClient(
            bootstrap_servers=config.kafka_bootstrap_servers
        )
        self.producer = KafkaProducer(bootstrap_servers=config.kafka_bootstrap_servers)
        self.sr_client = SchemaRegistryClient(url=config.schema_registry_url)
        self.serializer = AvroMessageSerializer(self.sr_client)

    def send_message(self, data: dict[str, Any]) -> None:
        if not (value_schema := self.sr_client.get_schema(self.subject)):
            print("Schema not found")  # noqa: T201
            return
        message = self.serializer.encode_record_with_schema_id(
            value_schema.schema_id, record=data
        )
        self.producer.send(topic=self.topic_name, value=message)
        print("Message sent")  # noqa: T201

    def create_topic(
        self,
        num_partitions: int = 1,
        replication_factor: int = 1,
        value_schema_validation: bool = True,
        key_schema_validation: bool = False,
    ) -> None:
        if not self.is_topic_exist():
            topic_configs = {}
            if key_schema_validation:
                # валидация ключа сообщения на соответствие схемы, название которой определяется в TopicNameStrategy
                topic_configs["confluent.key.schema.validation"] = "true"
            new_topic = NewTopic(
                name=self.topic_name,
                num_partitions=num_partitions,
                replication_factor=replication_factor,
                topic_configs=topic_configs,
            )
            print(self.kafka_admin_client.create_topics([new_topic]))  # noqa: T201
            print(f'Topic "{self.topic_name}" created')  # noqa: T201
        else:
            print(f'Topic "{self.topic_name}" already exist')  # noqa: T201

    def delete_topic(self) -> None:
        if self.is_topic_exist():
            print(  # noqa: T201
                self.kafka_admin_client.delete_topics([self.topic_name])
            )
            print(f'Topic "{self.topic_name}" deleted')  # noqa: T201
        else:
            print(f'Topic "{self.topic_name}" is not exist')  # noqa: T201

    def is_topic_exist(self) -> bool:
        return self.topic_name in self.kafka_admin_client.list_topics()

    def register_avro_schema(self, data: type[AvroModel]) -> None:
        schema = data.avro_schema()
        if self.get_latest_schema() is not None:
            if not self.sr_client.test_compatibility(
                subject=self.subject, schema=schema
            ):
                print(  # noqa: T201
                    "Schema is not backward compatible with the current version"
                )
                return
            print("Update existing schema")  # noqa: T201
        print(  # noqa: T201
            self.sr_client.register(subject=self.subject, schema=schema)
        )

    def get_latest_schema(self) -> AvroSchema | None:
        if schema := self.sr_client.get_schema(subject=self.subject):
            return schema.schema
        return None

    def get_versions(self) -> list[int]:
        return self.sr_client.get_versions(subject=self.subject)

    def get_subjects(self) -> list[str]:
        return self.sr_client.get_subjects()

    def get_compatibility_level(self) -> str:
        return self.sr_client.get_compatibility(subject=self.subject)

    def update_compatibility_level(self, level: str) -> None:
        if level in VALID_LEVELS:
            self.sr_client.update_compatibility(level=level, subject=self.subject)
        else:
            print(f"Level is not valid. Valid levels: {VALID_LEVELS}")  # noqa: T201

    def is_subject_exist(self) -> bool:
        return self.subject in self.sr_client.get_subjects()

    def shutdown(self) -> None:
        self.producer.close()
        self.kafka_admin_client.close()


if __name__ == "__main__":
    # установить флаг, обозначающий окружение
    IS_TEST = False

    # заменить на значения боевого окружения
    SR_URL = "http://localhost:8081"
    KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"

    # заменить на значения тестового окружения
    TEST_SR_URL = "http://localhost:8081"
    TEST_KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"

    topics: dict[type[AvroModel], tuple[str, str]] = {
        UserCreatedEvent: (
            "auth.user-stream",
            "auth.user-stream-value",
        ),
    }

    config = Config(
        kafka_bootstrap_servers=(
            TEST_KAFKA_BOOTSTRAP_SERVERS if IS_TEST else KAFKA_BOOTSTRAP_SERVERS
        ),
        schema_registry_url=TEST_SR_URL if IS_TEST else SR_URL,
    )

    for event, (topic_name, subject) in topics.items():
        kfk = KafkaAvroTopicHelper(
            topic_name=topic_name,
            subject=subject,
            config=config,
        )
        kfk.create_topic()
        kfk.register_avro_schema(event)
        kfk.shutdown()
