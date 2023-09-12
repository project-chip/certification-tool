from typing import Optional

import click
from api_lib_autogen.api_client import SyncApis
from client import client
from utils import __print_json

sync_apis = SyncApis(client)
test_run_execution_api = sync_apis.test_run_executions_api

table_format = "{:<5} {:30} {:10} {:40}"


@click.command()
@click.option(
    "--id",
    default=None,
    required=False,
    type=int,
    help="Fetch specific Test Run via ID",
)
@click.option(
    "--skip",
    default=None,
    required=False,
    type=int,
    help="The first N Test Runs to skip, ordered by ID",
)
@click.option(
    "--limit",
    default=None,
    required=False,
    type=int,
    help="Maximun number of test runs to fetch",
)
@click.option(
    "--json",
    is_flag=True,
    help="Print JSON response for more details",
)
def test_run_execution_history(
    id: Optional[int], skip: Optional[int], limit: Optional[int], json: Optional[bool]
) -> None:
    """Read test run execution history"""
    if id is not None:
        __test_run_execution_by_id(id, json)
    elif skip is not None or limit is not None:
        __test_run_execution_batch(json, skip, limit)
    else:
        __test_run_execution_batch(json)
    client.close()


def __test_run_execution_by_id(id: int, json: bool) -> None:
    test_run_execution = test_run_execution_api.read_test_run_execution_api_v1_test_run_executions_id_get(id=id)
    if json:
        __print_json(test_run_execution)
    else:
        __print_table_test_execution(test_run_execution.dict())


def __test_run_execution_batch(json: Optional[bool], skip: Optional[int] = None, limit: Optional[int] = None) -> None:
    test_run_executions = test_run_execution_api.read_test_run_executions_api_v1_test_run_executions_get(
        skip=skip, limit=limit
    )
    if json:
        __print_json(test_run_executions)
    else:
        __print_table_test_executions(test_run_executions)


def __print_table_test_executions(test_execution: list) -> None:
    __print_table_header()
    if isinstance(test_execution, list):
        for item_dict in test_execution:
            __print_table_test_execution(item_dict.dict(), print_header=False)


def __print_table_test_execution(item: dict, print_header=True) -> None:
    print_header and __print_table_header()
    click.echo(table_format.format(item.get("id"), item.get("title"), item.get("state"), item.get("error", "No Error")))


def __print_table_header() -> None:
    click.echo(table_format.format("ID", "Title", "State", "Error"))
