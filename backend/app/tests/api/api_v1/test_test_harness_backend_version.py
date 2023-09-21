from http import HTTPStatus

from fastapi.testclient import TestClient

from app.core.config import settings


def test_test_harness_backend_version(client: TestClient) -> None:
    """Get Test Runner status when test runner is idle."""
    response = client.get(f"{settings.API_V1_STR}/version")

    assert response.status_code == HTTPStatus.OK
    content = response.json()
    assert content["version"] is not None
    assert content["sha"] is not None
