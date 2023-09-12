# import sqlalchemy as JSONB
from typing import Any, Optional, Type

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, parse_obj_as
from sqlalchemy.types import JSON, TypeDecorator


class PydanticBaseType(TypeDecorator):
    """Pydantic type.
    SAVING:
    - Uses SQLAlchemy JSON type under the hood.
    - Accepts the pydantic model and converts it to a dict on save.
    - SQLAlchemy engine JSON-encodes the dict to a string.
    RETRIEVING:
    - Pulls the string from the database.
    - SQLAlchemy engine JSON-decodes the string to a dict.
    - Uses the dict to create a pydantic model.
    """

    impl = JSON

    def __init__(self, pydantic_type: Type[BaseModel]):
        super().__init__()
        self.pydantic_type = pydantic_type

    def process_bind_param(self, value: Any, _: Any) -> Any:
        return jsonable_encoder(value) if value is not None else None


class PydanticModelType(PydanticBaseType):
    def process_result_value(self, value: Any, _: Any) -> Optional[BaseModel]:
        if value is None:
            return None
        return parse_obj_as(self.pydantic_type, value)


class PydanticListType(PydanticBaseType):
    def process_result_value(self, value: Any, _: Any) -> Optional[list[BaseModel]]:
        if value is None:
            return None
        return parse_obj_as(
            list[self.pydantic_type], obj=value  # type: ignore[name-defined]
        )
