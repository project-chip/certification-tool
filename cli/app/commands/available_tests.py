from typing import Any

import click
import yaml
from api_lib_autogen.api_client import SyncApis
from click.exceptions import Exit
from client import client
from utils import __json_string, __print_json

sync_apis = SyncApis(client)


@click.command()
@click.option(
    "--json",
    is_flag=True,
    flag_value=True,
    help="Print JSON response for more details",
)
def available_tests(json: bool = False) -> None:
    """Get a list of available tests"""

    test_collections = sync_apis.test_collections_api.read_test_collections_api_v1_test_collections_get()

    if test_collections is None:
        click.echo("Server did not return test_collection", err=True)
        raise Exit(code=1)

    if json:
        __print_json(test_collections)
    else:
        __print_yaml(test_collections)
    client.close()


def __print_yaml(object: Any) -> None:
    click.echo(yaml.dump(yaml.load(__json_string(object), Loader=yaml.FullLoader)))
