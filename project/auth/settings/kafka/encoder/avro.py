import datetime
import fastavro
from settings.kafka.encoder.base import KafkaEncoder
from typing import Any
from schema_registry.client import AsyncSchemaRegistryClient
from schema_registry.client.utils import SchemaVersion
from schema_registry.serializers import AsyncAvroMessageSerializer


class KafkaAvroEncoder(KafkaEncoder):
    def __init__(
            self,
            topic_to_value_subject_map: dict[str, str],
            schema_registry_client: AsyncSchemaRegistryClient,
            serializer: AsyncAvroMessageSerializer,
    ) -> None:
        self._schema_registry_client = schema_registry_client
        self._topic_to_value_subject_map = topic_to_value_subject_map
        self._topic_to_key_subject_map = {}
        self._serializer = serializer
        fastavro.write.LOGICAL_WRITERS["string-iso8601_extended"] = encode_iso8601_extended

    async def encode_message(self, record: dict[str, Any], topic: str) -> bytes:
        value_schema_subject = self._get_value_schema_subject(topic)
        value_schema = await self._get_schema_from_registry(value_schema_subject)
        return await self._serializer.encode_record_with_schema_id(value_schema.schema_id, record=record)

    async def encode_key(self, key: dict[str, int] | None, topic: str) -> bytes | None:
        if key is None:
            return None

        if (key_schema_subject := self._get_key_schema_subject(topic)) is None:
            return None

        key_schema = await self._get_schema_from_registry(key_schema_subject)
        return await self._serializer.encode_record_with_schema_id(key_schema.schema_id, record=key)

    async def _get_schema_from_registry(self, subject: str) -> SchemaVersion:
        if not (schema := await self._schema_registry_client.get_schema(subject)):
            raise ValueError(f"couldn't get schema with subject {subject}")
        return schema

    def _get_value_schema_subject(self, topic: str) -> str:
        if not (value_schema_subject := self._topic_to_value_subject_map.get(topic)):
            raise ValueError(f"topic {topic} not mapped to value schema subject")
        return value_schema_subject

    def _get_key_schema_subject(self, topic: str) -> str | None:
        return self._topic_to_key_subject_map.get(topic)

def encode_iso8601_extended(value: datetime.datetime, *args: Any) -> str:
    tz_info = value.strftime("%z")
    tz_sign = tz_info[0]
    tz_hours_offset = tz_info[1:3]
    tz_minutes_offset = tz_info[3:]
    return (
        value.strftime("%Y%m%dT%H:%M:%S.%f")[:-3]
        + f"{tz_sign}{tz_hours_offset}:{tz_minutes_offset}"
    )
