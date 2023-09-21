from http import HTTPStatus

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.tests.utils.test_run_config import create_random_test_run_config


def test_create_test_run_config(client: TestClient, db: Session) -> None:
    data = {
        "name": "Foo",
        "dut_name": "Fighters",
        "selected_tests": {
            "sample_tests": {
                "SampleTestSuite1": {
                    "TCSS1001": 1,
                    "TCSS1002": 2,
                    "TCSS1003": 2,
                    "TCSS1004": 5,
                    "TCSS1005": 8,
                },
            },
        },
    }
    response = client.post(
        f"{settings.API_V1_STR}/test_run_configs/",
        json=data,
    )
    assert response.status_code == HTTPStatus.OK
    content = response.json()
    assert content["name"] == data["name"]
    assert content["dut_name"] == data["dut_name"]
    assert content["selected_tests"] == data["selected_tests"]
    assert "id" in content


def test_create_test_run_config_invalid_selection(
    client: TestClient, db: Session
) -> None:
    data = {
        "name": "Foo",
        "dut_name": "Fighters",
        "selected_tests": {
            "sample_tests": {
                "SampleTestSuite1": {
                    "TCSS1001": 1,
                    "TCSS1002": 2,
                    "TCSS1003": 2,
                    "TCSS1004": 5,
                    "Invalid": 8,
                },
            },
        },
    }
    response = client.post(
        f"{settings.API_V1_STR}/test_run_configs/",
        json=data,
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    content = response.json()
    assert "detail" in content


def test_read_test_run_config(client: TestClient, db: Session) -> None:
    test_run_config = create_random_test_run_config(db)
    response = client.get(
        f"{settings.API_V1_STR}/test_run_configs/{test_run_config.id}",
    )
    assert response.status_code == HTTPStatus.OK
    content = response.json()
    assert content["name"] == test_run_config.name
    assert content["dut_name"] == test_run_config.dut_name
    assert content["id"] == test_run_config.id
    assert content["selected_tests"] == test_run_config.selected_tests


def test_update_test_run_config(client: TestClient, db: Session) -> None:
    test_run_config = create_random_test_run_config(db)
    data = {"name": "Updated Name"}
    response = client.put(
        f"{settings.API_V1_STR}/test_run_configs/{test_run_config.id}",
        json=data,
    )
    assert response.status_code == HTTPStatus.OK
    content = response.json()
    assert content["name"] == data["name"]
    assert content["id"] == test_run_config.id
