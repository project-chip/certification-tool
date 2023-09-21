import json
from typing import Any, Generator

import pydantic.json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


def get_db() -> Generator:
    """Use a sessionmaker to return a DB session
    This method is used for DB dependency injection in the API and Test Engine related
    files to retrieve the default DB Session.
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def _pydantic_json_serializer(*args: Any, **kwargs: Any) -> str:
    """
    Support serializing pydantic models to json
    """
    return json.dumps(*args, default=pydantic.json.pydantic_encoder, **kwargs)


if settings.SQLALCHEMY_DATABASE_URI is None:
    raise ValueError("Database URI is missing")

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    json_serializer=_pydantic_json_serializer,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
