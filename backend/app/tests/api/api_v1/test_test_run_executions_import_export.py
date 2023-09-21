# type: ignore
# Ignore mypy type check for this file

import io
import json
from http import HTTPStatus
from unittest import mock

import pytest
from fastapi import HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder

from app import crud
from app.api.api_v1.endpoints.test_run_executions import (
    export_test_run_execution,
    import_test_run_execution,
)
from app.crud.crud_test_run_execution import ImportError
from app.models import TestRunExecution
from app.models.test_enums import TestStateEnum
from app.tests.utils.test_run_execution import test_run_execution_base_dict


def test_export_test_run_execution_with_a_not_found_test_execution_id() -> None:
    """
    Test operation of export test run execution with not found test execution id.
    """
    db_revision_test = "aabbccdd"  # spell-checker:disable-line
    not_found_test_execution_id = 99999

    with mock.patch(
        "app.version.version_information.db_revision", db_revision_test
    ), mock.patch("app.crud.test_run_execution.get", return_value=None), pytest.raises(
        HTTPException
    ) as e:
        export_test_run_execution(
            db=mock.MagicMock(),
            id=not_found_test_execution_id,
        )

    assert (
        e.value.detail
        == f"Test Run Execution with id {not_found_test_execution_id} not found"
    )
    assert e.value.status_code == HTTPStatus.NOT_FOUND


def test_export_test_run_execution_successfully() -> None:
    """
    Test operation of export test run execution runs successfully
    """
    db_revision_test = "aabbccdd"  # spell-checker:disable-line
    log = [
        {
            "level": "INFO",
            "timestamp": 1684878223.482982,
            "message": "Run Test Runner is Ready",
            "test_suite_execution_index": None,
            "test_case_execution_index": None,
            "test_step_execution_index": None,
        }
    ]
    execution_mock = TestRunExecution(
        title="Test Execution to Export",
        state=TestStateEnum.PASSED,
        created_at="2023-05-23T21:43:43.543147",
        log=log,
    )

    with mock.patch(
        "app.version.version_information.db_revision", db_revision_test
    ), mock.patch("app.crud.test_run_execution.get", return_value=execution_mock):
        exported_execution = export_test_run_execution(
            db=mock.MagicMock(),
            id=1,
        )
        json_exported = json.loads(jsonable_encoder(exported_execution.body))

        assert exported_execution.media_type == "application/json"
        assert json_exported["db_revision"] == db_revision_test
        assert json_exported["test_run_execution"]["title"] == execution_mock.title


def test_import_test_run_execution_with_missing_db_revision() -> None:
    """
    Test operation of import test run execution with a missing db revision
    """
    db_revision_test = "aabbccdd"  # spell-checker:disable-line

    imported_file_dict = {"test_run_execution": test_run_execution_base_dict}
    imported_file_content = json.dumps(imported_file_dict).encode("utf-8")

    file = io.BytesIO(imported_file_content)
    imported_file = UploadFile(file=file)

    with mock.patch(
        "app.version.version_information.db_revision",
        db_revision_test,
    ), pytest.raises(HTTPException) as e:
        import_test_run_execution(
            db=mock.MagicMock(), project_id=1, import_file=imported_file
        )

    assert "db_revision" in e.value.detail
    assert e.value.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_import_test_run_execution_with_missing_test_run_execution() -> None:
    """
    Test operation of import test run execution with a missing test run execution
    """
    db_revision_test = "aabbccdd"  # spell-checker:disable-line

    imported_file_dict = {"db_revision": "9996326cbd1d"}
    imported_file_content = json.dumps(imported_file_dict).encode("utf-8")

    file = io.BytesIO(imported_file_content)
    imported_file = UploadFile(file=file)

    with mock.patch(
        "app.version.version_information.db_revision",
        db_revision_test,
    ), pytest.raises(HTTPException) as e:
        import_test_run_execution(
            db=mock.MagicMock(), project_id=1, import_file=imported_file
        )

    assert "test_run_execution" in e.value.detail
    assert e.value.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_import_test_run_execution_db_revision_mismatch() -> None:
    """
    Test operation of import test run execution with a different db revision
    from backend
    """

    db_revision_test = "aabbccdd"  # spell-checker:disable-line

    imported_file_dict = {
        "db_revision": "9996326cbd1d",
        "test_run_execution": test_run_execution_base_dict,
    }
    imported_file_content = json.dumps(imported_file_dict).encode("utf-8")

    file = io.BytesIO(imported_file_content)
    imported_file = UploadFile(file=file)

    with mock.patch(
        "app.version.version_information.db_revision",
        db_revision_test,
    ), pytest.raises(HTTPException) as e:
        import_test_run_execution(
            db=mock.MagicMock(), project_id=1, import_file=imported_file
        )

    assert (
        e.value.detail == "Mismatching 'db_revision'. "
        f"Trying to import from 9996326cbd1d to {db_revision_test}"
    )
    assert e.value.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_import_test_run_execution_raises_HTTPException() -> None:
    """
    Test operation of import test run execution when it raises HTTPException
    """
    db_revision_test = "aabbccdd"  # spell-checker:disable-line

    imported_file_dict = {
        "db_revision": db_revision_test,
        "test_run_execution": test_run_execution_base_dict,
    }
    imported_file_content = json.dumps(imported_file_dict).encode("utf-8")

    file = io.BytesIO(imported_file_content)
    imported_file = UploadFile(file=file)

    with mock.patch(
        "app.version.version_information.db_revision",
        db_revision_test,
    ), mock.patch.object(
        target=crud.test_run_execution,
        attribute="import_execution",
        side_effect=ImportError("Import Exception raised"),
    ) as mock_import_execution, pytest.raises(
        HTTPException
    ) as e:
        import_test_run_execution(
            db=mock.MagicMock(), project_id=1, import_file=imported_file
        )
    assert e.value.detail == "Import Exception raised"
    assert e.value.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    mock_import_execution.assert_called_once()


def test_import_test_run_execution_successfully() -> None:
    """
    Test operation of import test run execution runs successfully
    """
    db_revision_test = "aabbccdd"  # spell-checker:disable-line

    imported_file_dict = {
        "db_revision": db_revision_test,
        "test_run_execution": test_run_execution_base_dict,
    }
    imported_file_content = json.dumps(imported_file_dict).encode("utf-8")

    file = io.BytesIO(imported_file_content)
    imported_file = UploadFile(file=file)

    execution_mock = TestRunExecution(title="Execution test")

    with mock.patch(
        "app.version.version_information.db_revision",
        db_revision_test,
    ), mock.patch.object(
        target=crud.test_run_execution,
        attribute="import_execution",
        return_value=execution_mock,
    ) as mock_import_execution:
        import_result = import_test_run_execution(
            db=mock.MagicMock(), project_id=1, import_file=imported_file
        )

        assert import_result.title == execution_mock.title

    mock_import_execution.assert_called_once()
