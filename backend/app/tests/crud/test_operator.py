from unittest import mock

from sqlalchemy.orm import Session

from app import crud
from app.models import Operator
from app.schemas.operator import OperatorCreate, OperatorUpdate
from app.tests.utils.operator import create_random_operator
from app.tests.utils.utils import random_lower_string


def test_create_operator(db: Session) -> None:
    name = random_lower_string()
    operator_in = OperatorCreate(name=name)
    operator = crud.operator.create(db=db, obj_in=operator_in)
    assert operator.name == name


def test_get_operator(db: Session) -> None:
    operator = create_random_operator(db=db)

    stored_operator = crud.operator.get(db=db, id=operator.id)
    assert stored_operator
    assert operator.id == stored_operator.id
    assert operator.name == stored_operator.name


def test_update_operator(db: Session) -> None:
    operator = create_random_operator(db=db)

    new_name = random_lower_string()
    operator_update = OperatorUpdate(name=new_name)

    updated_operator = crud.operator.update(
        db=db, db_obj=operator, obj_in=operator_update
    )

    assert operator.id == updated_operator.id
    assert updated_operator.name == new_name


def test_delete_operator(db: Session) -> None:
    operator = create_random_operator(db=db)

    operator2 = crud.operator.remove(db=db, id=operator.id)
    assert operator2 is not None
    assert operator2.id == operator.id
    assert operator2.name == operator.name

    operator3 = crud.operator.get(db=db, id=operator.id)
    assert operator3 is None


def test_get_or_create_existing_operator() -> None:
    mocked_db = mock.MagicMock()
    operator_id = 42
    operator_name = "John Doe"

    crud_operator = crud.crud_operator.CRUDOperator(Operator)

    with mock.patch.object(
        target=crud_operator,
        attribute="get_by_name",
        return_value=Operator(id=operator_id, name=operator_name),
    ) as mocked_get_by_name:
        id = crud_operator.get_or_create(db=mocked_db, name=operator_name, commit=True)

        mocked_get_by_name.assert_called_once_with(db=mocked_db, name=operator_name)
        assert id == operator_id


def test_get_or_create_non_existing_operator_commit_true() -> None:
    mocked_db = mock.MagicMock()
    operator_name = "John Doe"

    crud_operator = crud.crud_operator.CRUDOperator(Operator)

    with mock.patch.object(
        target=crud_operator,
        attribute="get_by_name",
        return_value=None,
    ) as mocked_get_by_name, mock.patch.object(
        target=mocked_db,
        attribute="add",
    ) as mocked_add, mock.patch.object(
        target=mocked_db,
        attribute="commit",
    ) as mocked_commit:
        _ = crud_operator.get_or_create(db=mocked_db, name=operator_name, commit=True)

        mocked_get_by_name.assert_called_once_with(db=mocked_db, name=operator_name)

        mocked_add.assert_called_once()
        assert isinstance(mocked_add.mock_calls[0].args[0], Operator)

        mocked_commit.assert_called_once()


def test_get_or_create_non_existing_operator_commit_false() -> None:
    mocked_db = mock.MagicMock()
    operator_name = "John Doe"

    crud_operator = crud.crud_operator.CRUDOperator(Operator)

    with mock.patch.object(
        target=crud_operator,
        attribute="get_by_name",
        return_value=None,
    ) as mocked_get_by_name, mock.patch.object(
        target=mocked_db,
        attribute="add",
    ) as mocked_add, mock.patch.object(
        target=mocked_db,
        attribute="commit",
    ) as mocked_commit:
        _ = crud_operator.get_or_create(db=mocked_db, name=operator_name, commit=False)

        mocked_get_by_name.assert_called_once_with(db=mocked_db, name=operator_name)

        mocked_add.assert_called_once()
        assert isinstance(mocked_add.mock_calls[0].args[0], Operator)

        mocked_commit.assert_not_called()
