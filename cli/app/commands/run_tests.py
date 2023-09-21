import asyncio
import datetime
import json

import api_lib_autogen.models as m
import click
import test_run.logging as test_logging
from api_lib_autogen.api_client import AsyncApis
from api_lib_autogen.exceptions import UnexpectedResponse
from async_cmd import async_cmd
from click.exceptions import Exit
from client import client
from test_run.websocket import TestRunSocket

async_apis = AsyncApis(client)
test_run_executions_api = async_apis.test_run_executions_api


@click.command()
@click.option(
    "--selected-tests",
    "-s",
    help="JSON string with selected tests. "
    'Format: \'{"collection_name":{"test_suite_id":{"test_case_id": <iterations>}}}\'',
)
@click.option(
    "--title", default=lambda: str(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")), show_default="timestamp"
)
@click.option("--file", "-f", help="JSON file location")
@click.option(
    "--project-id",
    required=True,
    help="Project ID that this test run belongs to",
)
@async_cmd
async def run_tests(selected_tests: str, title: str, file: str, project_id: int) -> None:
    """Create a new test run from selected tests"""

    # Configure new log output for test.
    log_path = test_logging.configure_logger_for_run(title=title)

    selected_tests_dict = __parse_selected_tests(selected_tests, file)

    new_test_run = await __create_new_test_run(selected_tests=selected_tests_dict, title=title, project_id=project_id)
    socket = TestRunSocket(new_test_run)
    socket_task = asyncio.create_task(socket.connect_websocket())
    new_test_run = await __start_test_run(new_test_run)
    socket.run = new_test_run
    await socket_task
    await client.aclose()
    click.echo(f"Log output in: '{log_path}'")


async def __create_new_test_run(selected_tests: dict, title: str, project_id: int) -> None:
    click.echo(f"Creating new test run with title: {title}")

    test_run_in = m.TestRunExecutionCreate(title=title, project_id=project_id)
    json_body = m.BodyCreateTestRunExecutionApiV1TestRunExecutionsPost(
        test_run_execution_in=test_run_in, selected_tests=selected_tests
    )

    try:
        return await test_run_executions_api.create_test_run_execution_api_v1_test_run_executions_post(json_body)
    except UnexpectedResponse as e:
        click.echo(f"Create test run execution failed {e.status_code}: {e.content}")
        raise Exit(code=1)


async def __start_test_run(test_run: m.TestRunExecutionWithChildren) -> m.TestRunExecutionWithChildren:
    click.echo(f"Starting Test run: Title: {test_run.title}, id: {test_run.id}")
    try:
        return await test_run_executions_api.start_test_run_execution_api_v1_test_run_executions_id_start_post(
            id=test_run.id
        )
    except UnexpectedResponse as e:
        click.echo(f"Failed to start test run: {e.status_code} {e.content}", err=True)
        raise Exit(code=1)


def __parse_selected_tests(json_str: str, filename: str) -> dict:
    try:
        if filename:
            json_file = open(filename, "r")
            json_str = json_file.read()
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        click.echo(f"Failed to parse JSON parameter: {e.msg}")
        raise Exit(code=1)
    except FileNotFoundError as e:
        click.echo(f"File not found: {e.filename} {e.strerror}.")
        raise Exit(code=1)
