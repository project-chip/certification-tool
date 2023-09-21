import json
from typing import Any

import click


def __print_json(object: Any) -> None:
    click.echo(__json_string(object))


def __json_string(object: Any) -> str:
    if object is None:
        return "None"
    if isinstance(object, list):
        return json.dumps([item.dict() for item in object], indent=4, default=str)
    else:
        return json.dumps(object.dict(), indent=4, default=str)
