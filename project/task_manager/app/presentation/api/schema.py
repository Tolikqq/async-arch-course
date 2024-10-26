
from typing import TypeVar, TypeAlias, Generic, Any
from pydantic import BaseModel, Field
from fastapi import status as http_status
_Model = TypeVar("_Model")

GenericResponse: TypeAlias = BaseModel


class DataResponse(GenericResponse, Generic[_Model]):
    data: _Model


class OkResponse(GenericResponse, Generic[_Model]):
    status: int = Field(..., title="Status code of request.", examples=[http_status.HTTP_200_OK])
    error: None = None
    payload: DataResponse[_Model] = Field(title="Payload data.")

    @classmethod
    def new(
        cls,
        *,
        status_code: int,
        model: type[_Model] | list[type[_Model]] | Any,
        data: _Model | Any,
    ) -> "OkResponse[_Model]":
        return cls[model](status=status_code, payload=DataResponse[model](data=data))  # type: ignore


SuccessEmptyResponse: OkResponse[BaseModel] = OkResponse.new(
    status_code=http_status.HTTP_200_OK, model=BaseModel, data={}
)