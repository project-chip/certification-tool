import logging

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, database_exists, drop_database

import alembic.config
from app.db import base  # noqa: F401

# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)
    pass


def drop_app_database(engine: Engine) -> None:
    logger.info(f"Dropping app database: {engine.url}")
    if database_exists(engine.url):
        drop_database(engine.url)


def create_app_database(engine: Engine) -> None:
    logger.info(f"Creating app database: {engine.url}")
    if not database_exists(engine.url):
        create_database(engine.url)


def migrate_app_database() -> None:
    logger.info("Running alembic upgrade head")
    alembicArgs = [
        "--raiseerr",
        "upgrade",
        "head",
    ]
    alembic.config.main(argv=alembicArgs)


def reset_app_db(engine: Engine) -> None:
    drop_app_database(engine)
    create_app_database(engine)
    migrate_app_database()
