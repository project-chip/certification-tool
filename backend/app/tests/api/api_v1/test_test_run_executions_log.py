import json
from http import HTTPStatus
from json import JSONDecodeError

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.tests.utils.test_runner import load_and_run_tool_unit_tests
from test_collections.tool_unit_tests.test_suite_expected import TestSuiteExpected
from test_collections.tool_unit_tests.test_suite_expected.tctr_expected_pass import (
    TCTRExpectedPass,
)


@pytest.mark.asyncio
async def test_test_run_execution_response_log(
    async_client: AsyncClient, db: Session
) -> None:
    _, run, _, _ = await load_and_run_tool_unit_tests(
        db, TestSuiteExpected, TCTRExpectedPass
    )

    run_db = run.test_run_execution
    id = run_db.id
    url = f"{settings.API_V1_STR}/test_run_executions/{id}/log"
    response = await async_client.get(url)

    assert response.status_code == HTTPStatus.OK

    content_disposition_header = response.headers.get("content-disposition")
    assert content_disposition_header is None

    content_type_header = response.headers.get("content-type")
    assert content_type_header is not None
    assert isinstance(content_type_header, str)
    assert content_type_header == "text/plain; charset=utf-8"

    response_log_lines = response.text.split("\n")
    # Downloaded file have empty line in the end.
    assert len(response_log_lines) - 1 == len(run_db.log)

    # check response is not JSON
    response_first_line = response_log_lines[0]
    with pytest.raises(JSONDecodeError):
        json.loads(response_first_line)

    # assert content
    original_first_line = run_db.log[0]
    assert original_first_line.message in response_first_line


@pytest.mark.asyncio
async def test_test_run_execution_download_log(
    async_client: AsyncClient, db: Session
) -> None:
    _, run, _, _ = await load_and_run_tool_unit_tests(
        db, TestSuiteExpected, TCTRExpectedPass
    )

    run_db = run.test_run_execution
    id = run_db.id
    url = f"{settings.API_V1_STR}/test_run_executions/{id}/log?download=true"
    response = await async_client.get(url)

    assert response.status_code == HTTPStatus.OK

    content_disposition_header = response.headers.get("content-disposition")
    assert content_disposition_header is not None
    assert isinstance(content_disposition_header, str)
    expected_filename = f"{id}-{run_db.title}.log"
    assert content_disposition_header == f'attachment; filename="{expected_filename}"'

    content_type_header = response.headers.get("content-type")
    assert content_type_header is not None
    assert isinstance(content_type_header, str)
    assert content_type_header == "text/plain; charset=utf-8"

    file_lines = response.text.split("\n")
    # Downloaded file have empty line in the end.
    assert len(file_lines) - 1 == len(run_db.log)

    # check response is not JSON
    file_first_line = file_lines[0]
    with pytest.raises(JSONDecodeError):
        json.loads(file_first_line)

    # assert content
    original_first_line = run_db.log[0]
    assert original_first_line.message in file_first_line


@pytest.mark.asyncio
async def test_test_run_execution_json_log(
    async_client: AsyncClient, db: Session
) -> None:
    _, run, _, _ = await load_and_run_tool_unit_tests(
        db, TestSuiteExpected, TCTRExpectedPass
    )

    run_db = run.test_run_execution
    id = run_db.id
    url = f"{settings.API_V1_STR}/test_run_executions/{id}/log?json_entries=true"
    response = await async_client.get(url)

    assert response.status_code == HTTPStatus.OK

    content_disposition_header = response.headers.get("content-disposition")
    assert content_disposition_header is None

    content_type_header = response.headers.get("content-type")
    assert content_type_header is not None
    assert isinstance(content_type_header, str)
    assert content_type_header == "text/plain; charset=utf-8"

    response_log_lines = response.text.split("\n")
    # Downloaded file have empty line in the end.
    assert len(response_log_lines) - 1 == len(run_db.log)

    # check response is JSON
    response_first_line = response_log_lines[0]
    parsed_line = json.loads(response_first_line)
    original_first_line = run_db.log[0]
    assert parsed_line == original_first_line
