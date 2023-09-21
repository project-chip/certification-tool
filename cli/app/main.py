#!/usr/bin/env python3


import click
from commands import (
    available_tests,
    create_project,
    delete_project,
    list_projects,
    run_tests,
    test_run_execution_history,
    update_project,
)


@click.group()
@click.version_option(version="0.0.1")
def root() -> None:
    pass


root.add_command(available_tests)
root.add_command(run_tests)
root.add_command(test_run_execution_history)
root.add_command(list_projects)
root.add_command(create_project)
root.add_command(delete_project)
root.add_command(update_project)


if __name__ == "__main__":
    root()
