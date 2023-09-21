import pytest
from sqlalchemy.orm import Session

from app import crud
from app.schemas.test_run_config import TestRunConfigUpdate
from app.tests.utils.test_run_config import create_random_test_run_config
from app.tests.utils.utils import random_lower_string


def test_create_test_run_config(db: Session) -> None:
    # Create build new test_run_config
    name = random_lower_string()
    dut_name = random_lower_string()
    selected_tests = {
        "sample_tests": {
            "SampleTestSuite1": {"TCSS1001": 1, "TCSS1002": 2, "TCSS1003": 3}
        }
    }
    test_run_config = create_random_test_run_config(
        db=db, name=name, dut_name=dut_name, selected_tests=selected_tests
    )

    # assert created db values match
    assert test_run_config.name == name
    assert test_run_config.dut_name == dut_name
    assert test_run_config.selected_tests == selected_tests


def test_get_test_run_config(db: Session) -> None:
    # Create build new test_run_config
    test_run_config = create_random_test_run_config(db=db)

    # load stored test_run_config from DB
    stored_test_run_config = crud.test_run_config.get(db=db, id=test_run_config.id)

    # assert stored values match
    assert stored_test_run_config
    assert test_run_config.id == stored_test_run_config.id
    assert test_run_config.name == stored_test_run_config.name
    assert test_run_config.dut_name == stored_test_run_config.dut_name
    assert test_run_config.selected_tests == stored_test_run_config.selected_tests


def test_update_test_run_config(db: Session) -> None:
    # Create build new test_run_config
    test_run_config = create_random_test_run_config(db=db)

    # Prepare an update:
    name_update = random_lower_string()
    test_run_config_update = TestRunConfigUpdate(name=name_update)

    # Perform update
    test_run_config_updated = crud.test_run_config.update(
        db=db, db_obj=test_run_config, obj_in=test_run_config_update
    )

    assert test_run_config_updated.id == test_run_config.id
    assert test_run_config_updated.name == test_run_config.name


def test_delete_test_run_config(db: Session) -> None:
    # Create build new test_run_config
    test_run_config = create_random_test_run_config(db=db)

    # Assert that remove is not supported
    with pytest.raises(crud.CRUDOperationNotSupported):
        crud.test_run_config.remove(db=db, id=test_run_config.id)
