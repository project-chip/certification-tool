from typing import Any

from sqlalchemy import MetaData
from sqlalchemy.orm import (
    MANYTOMANY,
    MANYTOONE,
    ONETOMANY,
    DeclarativeBase,
    Mapped,
    Session,
    declared_attr,
    object_session,
)

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class DBSessionError(Exception):
    pass


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convention)
    id: Mapped[int]

    def __init__(self, **kwargs: Any) -> None:
        """
        Custom initializer that allows nested children initialization.
        Only keys that are present as instance's class attributes are allowed.
        These could be, for example, any mapped columns or relationships.

        Code inspired from GitHub.
        Ref: https://github.com/tiangolo/fastapi/issues/2194#issuecomment-877489000
        """

        cls = self.__class__
        model_columns = self.__mapper__.columns
        relationships = self.__mapper__.relationships

        for key, val in kwargs.items():
            if not hasattr(cls, key):
                raise TypeError(f"Invalid keyword argument: {key}")

            if key in model_columns:
                setattr(self, key, val)
                continue

            if key in relationships:
                relation_dir = relationships[key].direction.name
                relation_cls = relationships[key].mapper.entity

                if relation_dir == ONETOMANY.name or relation_dir == MANYTOMANY.name:
                    instances = [
                        elem if isinstance(elem, relation_cls) else relation_cls(**elem)
                        for elem in val
                    ]
                    setattr(self, key, instances)
                elif relation_dir == MANYTOONE.name:
                    if isinstance(val, relation_cls):
                        setattr(self, key, val)
                    else:
                        setattr(self, key, relation_cls(**val))

    # Generate __tablename__ automatically
    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def obj_session(self) -> Session:
        session = object_session(self)
        if session is None:
            raise DBSessionError(f"DB object: {self} is not a Session")
        return session
