# type: ignore
# Ignore mypy type check for this file

import asyncio
from asyncio import sleep
from http import HTTPStatus

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.models import TestRunExecution
from app.models.test_enums import TestStateEnum
from app.test_engine import (
    TEST_ENGINE_ABORTING_TESTING_MESSAGE,
    TEST_ENGINE_BUSY_MESSAGE,
    TEST_ENGINE_NOT_ACTIVE_MESSAGE,
    TEST_RUN_ALREADY_EXECUTED_MESSAGE,
)
from app.test_engine.test_runner import TestRunner, TestRunnerState
from app.tests.test_engine.test_runner import load_test_run_for_test_cases
from app.tests.utils.operator import create_random_operator
from app.tests.utils.project import create_random_project
from app.tests.utils.test_run_config import create_random_test_run_config
from app.tests.utils.test_run_execution import (
    create_random_test_run_execution,
    create_random_test_run_execution_archived,
    create_random_test_run_execution_with_test_case_states,
    create_test_run_execution_with_some_test_cases,
)
from app.tests.utils.utils import random_lower_string
from app.tests.utils.validate_json_response import validate_json_response

faker = Faker()


def test_create_test_run_execution_with_test_run_config_succeeds(
    client: TestClient, db: Session
) -> None:
    """This unit test will test the create API for TestRunExecution.
    The selected tests are passed indirectly by reffering to a TestRunConfig.
    This is expected to succeed, and the API should respond with HTTP status 200 OK
    """

    test_run_config = create_random_test_run_config(db)
    title = "Foo"
    description = random_lower_string()
    json_data = {
        "test_run_execution_in": {
            "title": title,
            "description": description,
            "test_run_config_id": test_run_config.id,
        }
    }
    response = client.post(
        f"{settings.API_V1_STR}/test_run_executions/",
        json=json_data,
    )
    assert response.status_code == HTTPStatus.OK
    content = response.json()
    assert content["title"] == title
    assert content["description"] == description


def test_create_test_run_execution_with_test_run_config_and_selected_tests_fails(
    client: TestClient, db: Session
) -> None:
    """This is a negative unit test, that will test the create API for TestRunExecution.
    The selected tests are passed both:
    - directly in the json payload, and
    - by referencing a TestRunConfig

    The response is expected to be an error,
    as the API only supports one of these options at once.
    """
    test_run_config = create_random_test_run_config(db)
    title = "Foo"
    json_data = {
        "test_run_execution_in": {
            "title": title,
            "test_run_config_id": test_run_config.id,
        },
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
        f"{settings.API_V1_STR}/test_run_executions/",
        json=json_data,
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    content = response.json()
    assert isinstance(content, dict)
    assert content.get("detail") is not None


def test_create_test_run_execution_with_selected_tests_succeeds(
    client: TestClient, db: Session
) -> None:
    """This unit test will test the create API for TestRunExecution.
    The selected tests are passed directly in the json payload. This is expected to
    succeed, and the API should respond with HTTP status 200 OK
    """
    title = "Foo"
    description = random_lower_string()
    json_data = {
        "test_run_execution_in": {
            "title": title,
            "description": description,
        },
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
        f"{settings.API_V1_STR}/test_run_executions/",
        json=json_data,
    )
    assert response.status_code == HTTPStatus.OK
    content = response.json()
    assert isinstance(content, dict)
    assert content.get("title") == title
    assert content.get("description") == description


def test_create_test_run_execution_with_selected_tests_and_operator_succeeds(
    client: TestClient, db: Session
) -> None:
    """This unit test will test the create API for TestRunExecution.
    The selected tests are passed directly in the json payload. This is expected to
    succeed, and the API should respond with HTTP status 200 OK
    """
    title = "Foo"
    operator = create_random_operator(db)
    json_data = {
        "test_run_execution_in": {"title": title, "operator_id": operator.id},
        "selected_tests": {
            "sample_tests": {
                "SampleTestSuite1": {"TCSS1001": 1},
            },
        },
    }
    response = client.post(
        f"{settings.API_V1_STR}/test_run_executions/",
        json=json_data,
    )
    assert response.status_code == HTTPStatus.OK
    content = response.json()
    assert isinstance(content, dict)
    assert content.get("title") == title

    response_operator = content.get("operator")
    assert response_operator is not None
    assert "id" in response_operator
    assert response_operator["id"] == operator.id
    assert "name" in response_operator
    assert response_operator["name"] == operator.name


def test_read_multiple_test_run_executions(client: TestClient, db: Session) -> None:
    # We generate a random test run for this test.
    # To validate the statistics, we create the run with a random number of test cases
    # with a known amount being in a passed/pending state.
    # (A total between 4 and 20 test cases)
    test_case_states = {
        TestStateEnum.PASSED: faker.pyint(2, 10),
        TestStateEnum.PENDING: faker.pyint(2, 10),
    }
    test_case_count = sum(test_case_states.values())

    # Create random data for testing
    new_test_run_execution = create_random_test_run_execution_with_test_case_states(
        db, test_case_states
    )

    # Currently, our API uses pagination to only return part of the data.
    # This is implemented using skip and limit.
    # Default is skip = 0 and limit = 100, which will return the first 100 entries.
    # In our testing we create some new test data, these will always end up in the end
    # of the list, we compute the "offset" so that we're sure to get the latest records.
    count = db.scalar(select(func.count(TestRunExecution.id))) or 0
    offset = max(0, count - 100)

    response = client.get(
        f"{settings.API_V1_STR}/test_run_executions?skip={offset}",
    )

    assert response.status_code == HTTPStatus.OK
    content = response.json()
    assert isinstance(content, list)
    for test_run in content:
        assert test_run["title"] is not None
        assert test_run["test_case_stats"] is not None

        # Assert data of new test_run_execution
        if test_run["id"] == new_test_run_execution.id:
            assert test_run["title"] == new_test_run_execution.title
            assert test_run["state"] == new_test_run_execution.state
            assert test_run["started_at"] == new_test_run_execution.started_at
            assert test_run["completed_at"] == new_test_run_execution.completed_at

            # Assert stats of new test_run_execution
            stats = test_run["test_case_stats"]
            assert isinstance(stats, dict)
            assert stats["test_case_count"] == test_case_count
            for state, count in test_case_states.items():
                stats["states"][state.name] = count


def test_read_multiple_test_run_executions_by_archived(
    client: TestClient, db: Session
) -> None:
    test_run_execution = create_random_test_run_execution_archived(db)

    limit = db.scalar(select(func.count(TestRunExecution.id))) or 0

    response = client.get(
        f"{settings.API_V1_STR}/test_run_executions?limit={limit}",
    )
    assert response.status_code == HTTPStatus.OK
    content = response.json()
    assert isinstance(content, list)
    assert not any(test_run.get("id") == test_run_execution.id for test_run in content)

    response = client.get(
        f"{settings.API_V1_STR}/test_run_executions?limit={limit}&archived=true",
    )
    assert response.status_code == HTTPStatus.OK
    content = response.json()
    assert isinstance(content, list)
    assert any(test_run.get("id") == test_run_execution.id for test_run in content)


def test_read_multiple_test_run_executions_by_project(
    client: TestClient, db: Session
) -> None:
    project = create_random_project(db)
    test_run_execution = create_random_test_run_execution(db, project_id=project.id)

    response = client.get(
        f"{settings.API_V1_STR}/test_run_executions?project_id={project.id}",
    )
    assert response.status_code == HTTPStatus.OK
    content = response.json()
    assert isinstance(content, list)
    assert any(test_run.get("id") == test_run_execution.id for test_run in content)

    project2 = create_random_project(db)
    response = client.get(
        f"{settings.API_V1_STR}/test_run_executions?project_id={project2.id}",
    )
    assert response.status_code == HTTPStatus.OK
    content = response.json()
    assert isinstance(content, list)
    assert len(content) == 0


def test_read_multiple_test_run_executions_with_search_query(
    client: TestClient, db: Session
) -> None:
    title = "This is bananas"
    test_run_execution = create_random_test_run_execution(db, title=title)

    response = client.get(
        f"{settings.API_V1_STR}/test_run_executions?search_query=Bananas",
    )

    assert response.status_code == 200
    content = response.json()
    assert isinstance(content, list)
    assert any(test_run.get("id") == test_run_execution.id for test_run in content)

    response = client.get(
        f"{settings.API_V1_STR}/test_run_executions?search_query=Oranges",
    )

    assert response.status_code == 200
    content = response.json()
    assert isinstance(content, list)
    assert not any(test_run.get("id") == test_run_execution.id for test_run in content)


def test_read_test_run_execution(client: TestClient, db: Session) -> None:
    # We generate a random test run for this test.
    # To validate that all test cases are returned in the response,
    # we create the run with a random number of passed test cases (2-10)
    test_case_states = {TestStateEnum.PASSED: faker.pyint(2, 10)}
    test_case_count = sum(test_case_states.values())

    new_test_run_execution = create_random_test_run_execution_with_test_case_states(
        db, test_case_states
    )

    # Get variables for asserts
    new_first_test_suite_execution = new_test_run_execution.test_suite_executions[0]
    new_test_suite_metadata = new_first_test_suite_execution.test_suite_metadata
    new_first_test_case_execution = new_first_test_suite_execution.test_case_executions[
        0
    ]
    new_test_case_metadata = new_first_test_case_execution.test_case_metadata

    # Perform request
    response = client.get(
        f"{settings.API_V1_STR}/test_run_executions/{new_test_run_execution.id}",
    )

    assert response.status_code == HTTPStatus.OK
    content = response.json()
    assert isinstance(content, dict)

    # Assert Test Run Execution fields
    assert content["id"] == new_test_run_execution.id
    assert content["title"] == new_test_run_execution.title
    assert content["state"] == new_test_run_execution.state
    assert content["started_at"] == new_test_run_execution.started_at
    assert content["completed_at"] == new_test_run_execution.completed_at
    test_suite_executions = content["test_suite_executions"]

    # Assert nested Test Suite Execution fields
    assert isinstance(test_suite_executions, list)
    assert len(test_suite_executions) == len(
        new_test_run_execution.test_suite_executions
    )
    first_test_suite_execution = test_suite_executions[0]
    assert first_test_suite_execution["id"] == new_first_test_suite_execution.id
    assert first_test_suite_execution["state"] == new_first_test_suite_execution.state
    assert (
        first_test_suite_execution["public_id"]
        == new_first_test_suite_execution.public_id
    )

    # Assert Test Suite Metadata
    test_suite_metadata = first_test_suite_execution["test_suite_metadata"]
    assert isinstance(test_suite_metadata, dict)
    assert test_suite_metadata["public_id"] == new_test_suite_metadata.public_id
    assert test_suite_metadata["title"] == new_test_suite_metadata.title
    assert test_suite_metadata["description"] == new_test_suite_metadata.description
    assert test_suite_metadata["version"] == new_test_suite_metadata.version
    assert test_suite_metadata["source_hash"] == new_test_suite_metadata.source_hash
    assert test_suite_metadata["id"] == new_test_suite_metadata.id

    # Assert nested Test Case Executions
    test_case_executions = first_test_suite_execution["test_case_executions"]
    assert isinstance(test_case_executions, list)
    assert len(test_case_executions) == test_case_count

    first_test_case_execution = test_case_executions[0]
    assert isinstance(first_test_case_execution, dict)

    assert first_test_case_execution["id"] == new_first_test_case_execution.id
    assert first_test_case_execution["state"] == new_first_test_case_execution.state
    assert (
        first_test_case_execution["public_id"]
        == new_first_test_case_execution.public_id
    )

    assert isinstance(first_test_case_execution["test_step_executions"], list)

    # Assert Test Case Metadata
    test_case_metadata = first_test_case_execution["test_case_metadata"]
    assert isinstance(test_case_metadata, dict)
    assert test_case_metadata["public_id"] == new_test_case_metadata.public_id
    assert test_case_metadata["title"] == new_test_case_metadata.title
    assert test_case_metadata["description"] == new_test_case_metadata.description
    assert test_case_metadata["version"] == new_test_case_metadata.version
    assert test_case_metadata["source_hash"] == new_test_case_metadata.source_hash
    assert test_case_metadata["id"] == new_test_case_metadata.id


@pytest.mark.asyncio
async def test_test_run_execution_start(async_client: AsyncClient, db: Session) -> None:
    test_run_execution = create_test_run_execution_with_some_test_cases(db=db)

    # First attempt to start test run
    response = await async_client.post(
        f"{settings.API_V1_STR}/test_run_executions/{test_run_execution.id}/start",
    )

    # Assert 200 OK and that test run data is returned
    assert response.status_code == HTTPStatus.OK
    content = response.json()
    assert isinstance(content, dict)
    assert content["id"] == test_run_execution.id


@pytest.mark.asyncio
async def test_test_run_execution_busy(async_client: AsyncClient, db: Session) -> None:
    test_run_execution = create_test_run_execution_with_some_test_cases(db=db)

    # Start TestRunner (singleton)
    test_runner = TestRunner()
    test_runner.load_test_run(test_run_execution.id)
    run_task = asyncio.create_task(test_runner.run())

    # Yield event loop
    await sleep(0)

    # First attempt to start test run while test is running
    response = await async_client.post(
        f"{settings.API_V1_STR}/test_run_executions/{test_run_execution.id}/start",
    )

    # Assert 409 stats and a detail error message
    assert response.status_code == HTTPStatus.CONFLICT
    content = response.json()
    assert isinstance(content, dict)
    assert "detail" in content.keys()
    assert content["detail"] == TEST_ENGINE_BUSY_MESSAGE

    # Wait for test runner to complete
    await run_task

    # Attempt to start a test run again
    test_run_execution = create_test_run_execution_with_some_test_cases(db=db)
    response = await async_client.post(
        f"{settings.API_V1_STR}/test_run_executions/{test_run_execution.id}/start",
    )

    # Assert 200 OK and that test run data is returned
    assert response.status_code == HTTPStatus.OK
    content = response.json()
    assert isinstance(content, dict)
    assert content["id"] == test_run_execution.id


@pytest.mark.asyncio
async def test_test_run_execution_cancel_not_running(
    async_client: AsyncClient, db: Session
) -> None:
    # Request abort testing
    response = await async_client.post(
        f"{settings.API_V1_STR}/test_run_executions/abort-testing",
    )

    # Assert 409 stats and a detail error message
    assert response.status_code == HTTPStatus.CONFLICT
    content = response.json()
    assert isinstance(content, dict)
    assert "detail" in content.keys()
    assert content["detail"] == TEST_ENGINE_NOT_ACTIVE_MESSAGE


@pytest.mark.asyncio
async def test_test_run_execution_cancel(
    async_client: AsyncClient, db: Session
) -> None:
    test_run_execution = create_test_run_execution_with_some_test_cases(db=db)

    # Start TestRunner (singleton)
    test_runner = TestRunner()
    test_runner.load_test_run(test_run_execution.id)

    # Save test_run reference to inspect models after completion
    test_run = test_runner.test_run
    assert test_run is not None

    run_task = asyncio.create_task(test_runner.run())

    # Yield event loop
    await sleep(0)

    # Request abort testing
    response = await async_client.post(
        f"{settings.API_V1_STR}/test_run_executions/abort-testing",
    )

    # Assert 200 OK and that detail is provided
    assert response.status_code == HTTPStatus.OK
    content = response.json()
    assert isinstance(content, dict)
    assert "detail" in content.keys()
    assert content["detail"] == TEST_ENGINE_ABORTING_TESTING_MESSAGE

    # Wait for run to complete
    await run_task

    # We don't know how far the testing got, but the last test_suite and test_case
    # should be cancelled
    last_test_suite = test_run.test_suites[-1]
    assert last_test_suite is not None
    assert last_test_suite.state == TestStateEnum.CANCELLED

    last_test_case = last_test_suite.test_cases[-1]
    assert last_test_case is not None
    assert last_test_case.state == TestStateEnum.CANCELLED


@pytest.mark.asyncio
async def test_test_run_execution_rerun_error(
    async_client: AsyncClient, db: Session
) -> None:
    """Start executing a test_run_execution that has already been executed.

    This is expected to fail and the API is expected to throw an error.

    Args:
        async_client (AsyncClient): HTTP client fixture for performing API calls.
        db (Session): Database fixture for creating test data.
    """

    test_run_execution = create_test_run_execution_with_some_test_cases(db=db)

    # Execute test run once
    test_runner = TestRunner()
    test_runner.load_test_run(test_run_execution.id)
    await test_runner.run()

    # Attempt to start test run again
    response = await async_client.post(
        f"{settings.API_V1_STR}/test_run_executions/{test_run_execution.id}/start"
    )

    # Assert 409 stats and a detail error message
    assert response.status_code == HTTPStatus.CONFLICT
    content = response.json()
    assert isinstance(content, dict)
    assert "detail" in content.keys()
    assert content["detail"] == TEST_RUN_ALREADY_EXECUTED_MESSAGE


@pytest.mark.asyncio
async def test_remove_test_run_execution_success(
    async_client: AsyncClient, db: Session
) -> None:
    """
    Test the removal of test run execution
    """
    operator = create_random_operator(db)
    test_run_execution = create_test_run_execution_with_some_test_cases(
        db=db, operator_id=operator.id
    )

    # Execute test run once
    test_runner = TestRunner()
    test_runner.load_test_run(test_run_execution.id)
    await test_runner.run()
    assert test_runner.state == TestRunnerState.IDLE

    # Remove test run execution
    response = await async_client.delete(
        f"{settings.API_V1_STR}/test_run_executions/{test_run_execution.id}",
    )

    # Assert 200 OK and that test run data is returned
    assert response.status_code == HTTPStatus.OK
    content = response.json()
    assert isinstance(content, dict)
    assert content["id"] == test_run_execution.id

    response = await async_client.delete(
        f"{settings.API_V1_STR}/test_run_executions/{test_run_execution.id}",
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_remove_test_run_execution_failed_running(
    async_client: AsyncClient, db: Session
) -> None:
    """
    Test the removal of test run execution when test run is still running
    """
    test_run_execution = create_test_run_execution_with_some_test_cases(db=db)

    # Execute test run once
    test_runner = TestRunner()
    test_runner.load_test_run(test_run_execution.id)

    run_task = asyncio.create_task(test_runner.run())

    # Yield the run loop to allow run task to be scheduled now
    # See https://docs.python.org/3.10/library/asyncio-task.html#sleeping
    await asyncio.sleep(0)

    assert test_runner.state == TestRunnerState.RUNNING

    # Remove test run execution
    response = await async_client.delete(
        f"{settings.API_V1_STR}/test_run_executions/{test_run_execution.id}",
    )

    # Assert 409 test run still running
    assert response.status_code == HTTPStatus.CONFLICT

    # Ensure test runner finishes before next unit test
    await run_task


def test_test_runner_status_idle(client: TestClient) -> None:
    """Get Test Runner status when test runner is idle."""
    response = client.get(f"{settings.API_V1_STR}/test_run_executions/status")

    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.OK,
        expected_content={"state": "idle"},
        dissalowed_keys=["test_run_execution"],
    )


@pytest.mark.asyncio
async def test_test_runner_status_running(
    async_client: AsyncClient, db: Session
) -> None:
    selected_tests = {
        "tool_unit_tests": {
            "TestSuiteExpected": {"TCTRExpectedPass": 1},
        }
    }

    test_runner = load_test_run_for_test_cases(db=db, test_cases=selected_tests)

    # Start running tests (async)
    run_task = asyncio.create_task(test_runner.run())

    # Yield the run loop to allow run task to be scheduled now
    # See https://docs.python.org/3.10/library/asyncio-task.html#sleeping
    await asyncio.sleep(0)

    assert test_runner.state == TestRunnerState.RUNNING

    response = await async_client.get(
        f"{settings.API_V1_STR}/test_run_executions/status"
    )

    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.OK,
        expected_content={"state": "running"},
        expected_keys=["test_run_execution_id"],
    )

    # Ensure test runner finishes before next unit test
    await run_task


def test_archive_project(client: TestClient, db: Session) -> None:
    test_run_execution = create_random_test_run_execution(db)
    response = client.post(
        f"{settings.API_V1_STR}/test_run_executions/{test_run_execution.id}/archive"
    )
    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.OK,
        expected_content={"id": test_run_execution.id},
        expected_keys=["archived_at"],
    )


def test_unarchive_test_run_execution(client: TestClient, db: Session) -> None:
    test_run_execution = create_random_test_run_execution(db)
    response = client.post(
        f"{settings.API_V1_STR}/test_run_executions/{test_run_execution.id}/unarchive"
    )
    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.OK,
        expected_content={
            "id": test_run_execution.id,
            "archived_at": None,
        },
    )


def test_archive_project_with_description(client: TestClient, db: Session) -> None:
    description = random_lower_string()
    test_run_execution = create_random_test_run_execution(db, description=description)
    response = client.post(
        f"{settings.API_V1_STR}/test_run_executions/{test_run_execution.id}/archive"
    )
    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.OK,
        expected_content={"id": test_run_execution.id, "description": description},
        expected_keys=["archived_at", "description"],
    )


def test_unarchive_test_run_execution_description(
    client: TestClient, db: Session
) -> None:
    description = random_lower_string()
    test_run_execution = create_random_test_run_execution(db, description=description)
    response = client.post(
        f"{settings.API_V1_STR}/test_run_executions/{test_run_execution.id}/unarchive"
    )
    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.OK,
        expected_content={
            "id": test_run_execution.id,
            "archived_at": None,
            "description": description,
        },
        expected_keys=["description"],
    )


def test_operations_missing_test_run(client: TestClient, db: Session) -> None:
    """Test HTTP errors when attempting operations on an invalid record id.

    Will create and delete a test run, to ensure the id is invalid."""
    test_run = create_random_test_run_execution(db)
    id = test_run.id
    crud.test_run_execution.remove(db=db, id=id)

    # Get
    response = client.get(f"{settings.API_V1_STR}/test_run_executions/{id}")
    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.NOT_FOUND,
        expected_keys=["detail"],
    )

    # Delete
    response = client.delete(f"{settings.API_V1_STR}/test_run_executions/{id}")
    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.NOT_FOUND,
        expected_keys=["detail"],
    )

    # Archive
    response = client.post(f"{settings.API_V1_STR}/test_run_executions/{id}/archive")
    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.NOT_FOUND,
        expected_keys=["detail"],
    )

    # Unarchive
    response = client.post(f"{settings.API_V1_STR}/test_run_executions/{id}/unarchive")
    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.NOT_FOUND,
        expected_keys=["detail"],
    )

    # Start Run
    response = client.post(f"{settings.API_V1_STR}/test_run_executions/{id}/start")
    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.NOT_FOUND,
        expected_keys=["detail"],
    )

    # Download log
    response = client.get(f"{settings.API_V1_STR}/test_run_executions/{id}/log")
    validate_json_response(
        response=response,
        expected_status_code=HTTPStatus.NOT_FOUND,
        expected_keys=["detail"],
    )
