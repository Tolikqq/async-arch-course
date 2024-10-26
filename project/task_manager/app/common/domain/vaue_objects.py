import uuid


class GenericUUID(uuid.UUID):
    @classmethod
    def next_id(cls) -> uuid.UUID:
        return uuid.uuid4()

