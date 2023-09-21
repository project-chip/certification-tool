from http import HTTPStatus
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.default_environment_config import default_environment_config
from app.models.project import Project
from app.schemas.test_environment_config import DutPairingModeEnum
from app.tests.utils.project import (
    create_random_project,
    create_random_project_archived,
)
from app.tests.utils.test_pics_data import create_random_project_with_pics
from app.tests.utils.validate_json_response import validate_json_response


def test_create_project_default_config(client: TestClient) -> None:
    data: dict[str, Any] = {"name": "Foo"}
    response = client.post(
        f"{settings.API_V1_STR}/projects/",
        json=data,
    )

    expected_data = data
    expected_data["config"] = default_environment_config

    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.OK,
        expected_content=expected_data,
        expected_keys=["id", "created_at", "updated_at", "config"],
    )


def test_create_project_custom_config(client: TestClient) -> None:
    custom_config = default_environment_config.copy(deep=True)
    custom_config.dut_config.pairing_mode = DutPairingModeEnum.BLE_THREAD
    data: dict[str, Any] = {"name": "Foo", "config": custom_config.dict()}
    response = client.post(
        f"{settings.API_V1_STR}/projects/",
        json=data,
    )

    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.OK,
        expected_content=data,
        expected_keys=["id", "created_at", "updated_at", "config"],
    )


def test_default_project_config(client: TestClient) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/projects/default_config",
    )

    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.OK,
        expected_content=default_environment_config.dict(),
    )


def test_read_project(client: TestClient, db: Session) -> None:
    project = create_random_project(db)
    response = client.get(
        f"{settings.API_V1_STR}/projects/{project.id}",
    )

    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.OK,
        expected_content={
            "id": project.id,
            "name": project.name,
        },
        expected_keys=["created_at", "updated_at"],
    )


def test_read_multiple_project(client: TestClient, db: Session) -> None:
    project1 = create_random_project(db)
    project2 = create_random_project(db)
    limit = db.scalar(select(func.count(Project.id))) or 0
    response = client.get(
        f"{settings.API_V1_STR}/projects?limit={limit}",
    )
    assert response.status_code == HTTPStatus.OK
    content = response.json()
    assert isinstance(content, list)
    assert any(project.get("id") == project1.id for project in content)
    assert any(project.get("id") == project2.id for project in content)


def test_read_multiple_project_by_archived(client: TestClient, db: Session) -> None:
    archived = create_random_project_archived(db)
    limit = db.scalar(select(func.count(Project.id))) or 0

    response = client.get(
        f"{settings.API_V1_STR}/projects?limit={limit}",
    )
    assert response.status_code == HTTPStatus.OK
    content = response.json()
    assert isinstance(content, list)
    assert not any(project.get("id") == archived.id for project in content)

    response = client.get(
        f"{settings.API_V1_STR}/projects?limit={limit}&archived=true",
    )
    assert response.status_code == HTTPStatus.OK
    content = response.json()
    assert isinstance(content, list)
    assert any(project.get("id") == archived.id for project in content)


def test_update_project(client: TestClient, db: Session) -> None:
    project = create_random_project(db)
    data = {"name": "Updated Name"}
    response = client.put(
        f"{settings.API_V1_STR}/projects/{project.id}",
        json=data,
    )

    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.OK,
        expected_content={
            "id": project.id,
            "name": data["name"],
        },
    )


def test_delete_project(client: TestClient, db: Session) -> None:
    project = create_random_project(db)
    response = client.delete(f"{settings.API_V1_STR}/projects/{project.id}")
    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.OK,
        expected_content={
            "id": project.id,
            "name": project.name,
        },
    )


def test_archive_project(client: TestClient, db: Session) -> None:
    project = create_random_project(db)
    response = client.post(f"{settings.API_V1_STR}/projects/{project.id}/archive")
    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.OK,
        expected_content={
            "id": project.id,
            "name": project.name,
        },
        expected_keys=["archived_at"],
    )


def test_unarchive_project(client: TestClient, db: Session) -> None:
    project = create_random_project(db)
    response = client.post(f"{settings.API_V1_STR}/projects/{project.id}/unarchive")
    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.OK,
        expected_content={
            "id": project.id,
            "name": project.name,
            "archived_at": None,
        },
    )


def test_operations_missing_test_run(client: TestClient, db: Session) -> None:
    """Test HTTP errors when attempting operations on an invalid record id.

    Will create and delete a project, to ensure the id is invalid."""
    test_run = create_random_project(db)
    id = test_run.id
    crud.project.remove(db=db, id=id)

    # Get
    response = client.get(f"{settings.API_V1_STR}/projects/{id}")
    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.NOT_FOUND,
        expected_keys=["detail"],
    )

    # Update
    response = client.put(
        f"{settings.API_V1_STR}/projects/{id}",
        json={"name": "Updated Name"},
    )
    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.NOT_FOUND,
        expected_keys=["detail"],
    )

    # Delete
    response = client.delete(f"{settings.API_V1_STR}/projects/{id}")
    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.NOT_FOUND,
        expected_keys=["detail"],
    )

    # Archive
    response = client.post(f"{settings.API_V1_STR}/projects/{id}/archive")
    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.NOT_FOUND,
        expected_keys=["detail"],
    )

    # Unarchive
    response = client.post(f"{settings.API_V1_STR}/projects/{id}/unarchive")
    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.NOT_FOUND,
        expected_keys=["detail"],
    )


def test_upload_pics(client: TestClient, db: Session) -> None:
    project = create_random_project(db)
    pics_file = Path(__file__).parent.parent.parent / "utils" / "test_pics.xml"
    upload_files = {"file": pics_file.read_text()}
    response = client.put(
        f"{settings.API_V1_STR}/projects/{project.id}/upload_pics",
        files=upload_files,
    )

    content = response.json()
    assert content["pics"] is not None


def test_pics_cluster_type(client: TestClient, db: Session) -> None:
    project = create_random_project_with_pics(db=db)

    cluster_name = "On/Off"
    pics_cluster_type_url = (
        f"{settings.API_V1_STR}/projects/{project.id}/pics_cluster_type"
        f"?cluster_name={cluster_name}"
    )

    response = client.delete(pics_cluster_type_url)

    content = response.json()
    assert content["pics"] is not None
    assert len(content["pics"]["clusters"]) == 0


def test_applicable_test_cases(client: TestClient, db: Session) -> None:
    project = create_random_project_with_pics(db=db)
    # retrieve applicable test cases
    response = client.get(
        f"{settings.API_V1_STR}/projects/{project.id}/applicable_test_cases",
    )

    content = response.json()
    assert content["test_cases"] is not None
    assert len(content["test_cases"]) > 0
    assert "TC_Pics (Test)" in content["test_cases"]


def test_applicable_test_cases_empty_pics(client: TestClient, db: Session) -> None:
    project = create_random_project(db)

    # retrieve applicable test cases
    response2 = client.get(
        f"{settings.API_V1_STR}/projects/{project.id}/applicable_test_cases",
    )

    content = response2.json()
    assert content["test_cases"] is not None
    # the project is created with empty pics
    # expected value: applicable_test_cases == 0
    assert len(content["test_cases"]) == 0
