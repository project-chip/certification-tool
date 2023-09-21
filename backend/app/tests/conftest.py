import asyncio
from typing import AsyncGenerator, Generator
from unittest import mock

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from fastapi.testclient import TestClient
from filelock import FileLock
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.base_class import Base
from app.db.init_db import create_app_database
from app.main import app as main_app
from app.test_engine import test_script_manager
from app.test_engine.test_collection_discovery import discover_test_collections

if settings.SQLALCHEMY_DATABASE_URI is None:
    raise ValueError("Database URI is missing")

test_engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI + "_test",
    pool_pre_ping=True,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def pytest_configure() -> None:
    """Initial pre-run Pytest configuration
    This is called by all the Pytest workers before starting the test session.
    It will create, if it does not exist, a test DB with all the metadata.
    NOTE: Since we don't want to call the DB creation from multiple workers at the same
    time, we are using a FileLock to prevent DB duplication errors.
    """
    with FileLock("test_db_creation.lock"):
        create_app_database(test_engine)
        Base.metadata.create_all(bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def default_to_test_db_session() -> Generator:
    """Override the DB Session maker to use Test DB.
    NOTE: This fixture will be autoused by all tests.
    """
    with mock.patch("app.db.session.SessionLocal", TestingSessionLocal):
        yield


@pytest.fixture(scope="session")
def db() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    yield session
    session.close()


# Create a new application for testing
@pytest.fixture(scope="session")
def app(event_loop: asyncio.AbstractEventLoop) -> Generator[FastAPI, None, None]:
    yield main_app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest_asyncio.fixture
async def async_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with LifespanManager(app):
        async with AsyncClient(
            app=app,
            base_url="http://testserver",
            headers={"Content-Type": "application/json"},
        ) as client:
            yield client


@pytest.fixture(autouse=True)
def block_on_serial_marker(request: pytest.FixtureRequest) -> Generator:
    """Used to ensure tests marked as serial, are not run on multiple workers.

    This fixture is applied to all tests, but only blocking using FileLock, for tests
    that are marked serial using: @pytest.mark.serial
    """
    if request.node.get_closest_marker("serial"):
        with FileLock("SerialTests.lock"):
            yield
    else:
        yield


"""
By default, test_script_manager does not discover all test collections including
unit tests. Make sure we discover all test collections here.
"""
test_script_manager.test_script_manager.test_collections = discover_test_collections(
    disabled_collections=None
)
