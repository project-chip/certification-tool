from http import HTTPStatus

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud import operator as crud_operator
from app.tests.utils.operator import create_random_operator
from app.tests.utils.validate_json_response import validate_json_response


def test_create_operator(client: TestClient, db: Session) -> None:
    data = {"name": "Foo"}
    response = client.post(
        f"{settings.API_V1_STR}/operators/",
        json=data,
    )
    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.OK,
        expected_content=data,
        expected_keys=["id"],
    )


def test_read_operator(client: TestClient, db: Session) -> None:
    operator = create_random_operator(db)
    response = client.get(
        f"{settings.API_V1_STR}/operators/{operator.id}",
    )

    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.OK,
        expected_content={"id": operator.id, "name": operator.name},
    )


def test_read_multiple_operators(client: TestClient, db: Session) -> None:
    _ = create_random_operator(db)
    _ = create_random_operator(db)
    _ = create_random_operator(db)

    response = client.get(
        f"{settings.API_V1_STR}/operators",
    )
    assert response.status_code == HTTPStatus.OK
    content = response.json()

    assert isinstance(content, list)
    assert len(content) > 2

    # assert default order is by id
    for i in range(0, len(content) - 1):
        op1 = content[i]
        op2 = content[i + 1]
        assert isinstance(op1, dict)
        assert isinstance(op2, dict)
        assert "id" in op1
        assert "id" in op2
        assert op1["id"] < op2["id"]


def test_update_operator(client: TestClient, db: Session) -> None:
    operator = create_random_operator(db)
    data = {"name": "Updated Name"}
    response = client.put(
        f"{settings.API_V1_STR}/operators/{operator.id}",
        json=data,
    )
    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.OK,
        expected_content={"id": operator.id, "name": data["name"]},
    )


def test_delete_operator(client: TestClient, db: Session) -> None:
    operator = create_random_operator(db)
    response = client.delete(f"{settings.API_V1_STR}/operators/{operator.id}")

    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.OK,
        expected_content={"id": operator.id, "name": operator.name},
    )

    # Remove in-memory instance from Session, so later crud operation
    # will not use stale data from this db session
    db.expunge(operator)
    assert crud_operator.get(db, operator.id) is None


def test_read_operator_not_found(client: TestClient, db: Session) -> None:
    operator_id = __not_found_operator_id(db)
    response = client.get(
        f"{settings.API_V1_STR}/operators/{operator_id}",
    )
    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.NOT_FOUND,
        expected_keys=["detail"],
    )


def test_update_operator_not_found(client: TestClient, db: Session) -> None:
    operator_id = __not_found_operator_id(db)
    data = {"name": "Updated Name"}
    response = client.put(
        f"{settings.API_V1_STR}/operators/{operator_id}",
        json=data,
    )
    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.NOT_FOUND,
        expected_keys=["detail"],
    )


def test_delete_operator_not_found(client: TestClient, db: Session) -> None:
    operator_id = __not_found_operator_id(db)
    response = client.delete(f"{settings.API_V1_STR}/operators/{operator_id}")
    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.NOT_FOUND,
        expected_keys=["detail"],
    )


def __not_found_operator_id(db: Session) -> int:
    operator = create_random_operator(db)
    crud_operator.remove(db, id=operator.id)
    return operator.id
