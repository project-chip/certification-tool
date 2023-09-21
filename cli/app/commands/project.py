import json
from typing import Any, List, Optional

import click
from api_lib_autogen.api_client import SyncApis
from api_lib_autogen.exceptions import UnexpectedResponse
from api_lib_autogen.models import Project, ProjectCreate, ProjectUpdate, TestEnvironmentConfig
from click.exceptions import Exit
from client import client
from pydantic import ValidationError
from utils import __print_json

sync_apis = SyncApis(client)

TABLE_FORMAT = "{:<5} {:20} {:40}"


@click.command()
@click.option(
    "--name",
    required=True,
    type=str,
    help="*Name of the project*",
)
@click.option(
    "--config",
    required=False,
    type=str,
    default=None,
    help="Config file for the project",
)
def create_project(name: str, config: Optional[str]) -> None:
    """Create a project"""
    try:
        test_environment_config = None
        if config is not None:
            file = open(config, "r")
            config_dict = json.load(file)
            test_environment_config = TestEnvironmentConfig(**config_dict)
        projectCreate = ProjectCreate(name=name, config=test_environment_config)
        response = sync_apis.projects_api.create_project_api_v1_projects_post(project_create=projectCreate)
    except json.JSONDecodeError as e:
        click.echo(f"Failed to parse JSON parameter: {e.msg}", err=True)
        raise Exit(code=1)
    except FileNotFoundError as e:
        click.echo(f"File not found: {e.filename} {e.strerror}", err=True)
        raise Exit(code=1)
    except ValidationError as e:
        click.echo(f"Validation failed for Config file: \n{e.json()}", err=True)
        raise Exit(code=1)
    except UnexpectedResponse as e:
        click.echo(f"Failed to create project {name}: {e.status_code} {e.content}", err=True)
        raise Exit(code=1)

    click.echo(f"Project {response.name} created with id {response.id}.")
    client.close()


@click.command()
@click.option(
    "--id",
    required=True,
    type=int,
    help="*Project Id to delete*",
)
def delete_project(id: int) -> None:
    """Delete a project"""
    try:
        sync_apis.projects_api.delete_project_api_v1_projects_id_delete(id=id)
    except UnexpectedResponse as e:
        click.echo(f"Failed to delete project {id}: {e.status_code} {e.content}", err=True)
        raise Exit(code=1)
    click.echo(f"Project {id} is deleted.")
    client.close()


@click.command()
@click.option(
    "--id",
    default=None,
    required=False,
    type=int,
    help="Fetch specific project via ID",
)
@click.option(
    "--archived",
    default=False,
    required=False,
    type=bool,
    help="List archived projects or not",
)
@click.option(
    "--skip",
    default=None,
    required=False,
    type=int,
    help="The first N projects to skip, ordered by ID",
)
@click.option(
    "--limit",
    default=None,
    required=False,
    type=int,
    help="Maximun number of projects to fetch",
)
@click.option(
    "--json",
    is_flag=True,
    flag_value=True,
    help="Print JSON response for more details",
)
def list_projects(
    id: Optional[int], archived: Optional[bool], skip: Optional[int], limit: Optional[int], json: Optional[bool]
) -> None:
    """Get a list of projects"""

    def __list_project_by_id(id: int) -> Project:
        try:
            return sync_apis.projects_api.read_project_api_v1_projects_id_get(id=id)
        except UnexpectedResponse as e:
            click.echo(f"Failed to list project {id}: {e.status_code} {e.content}", err=True)
            raise Exit(code=1)

    def __list_project_by_batch(
        archived: bool, skip: Optional[int] = None, limit: Optional[int] = None
    ) -> List[Project]:
        try:
            return sync_apis.projects_api.read_projects_api_v1_projects_get(archived=archived, skip=skip, limit=limit)
        except UnexpectedResponse as e:
            click.echo(f"Failed to list objects: {e.status_code} {e.content}", err=True)
            raise Exit(code=1)

    def __print_table(projects: Any) -> None:
        click.echo(
            TABLE_FORMAT.format(
                "ID",
                "Project Name",
                "Updated Time",
            )
        )

        if isinstance(projects, list):
            for item in projects:
                __print_project(item.dict())

        if isinstance(projects, Project):
            __print_project(projects.dict())

        click.echo("\nFor more information, please use --json\n")

    def __print_project(project: dict) -> None:
        click.echo(
            TABLE_FORMAT.format(
                project.get("id"),
                project.get("name"),
                str(project.get("updated_at")),
            )
        )

    if id is not None:
        projects = __list_project_by_id(id)
    else:
        projects = __list_project_by_batch(archived, skip, limit)

    if projects is None or len(projects) == 0:
        click.echo("Server did not return any project", err=True)
        raise Exit(code=1)

    if json:
        __print_json(projects)
    else:
        __print_table(projects)
    client.close()


@click.command()
@click.option(
    "--id",
    required=True,
    type=int,
    help="*The ID for the project to update*",
)
@click.option(
    "--config",
    required=True,
    type=str,
    help="New config file path",
)
def update_project(id: int, config: str):
    """Updates project with full test environment config file"""
    try:
        file = open(config, "r")
        config_dict = json.load(file)
        projectUpdate = ProjectUpdate(**config_dict)
        response = sync_apis.projects_api.update_project_api_v1_projects_id_put(id=id, project_update=projectUpdate)
        click.echo(f"Project {response.name} is updated with the new config.")
        client.close()
    except json.JSONDecodeError as e:
        click.echo(f"Failed to parse JSON parameter: {e.msg}", err=True)
        raise Exit(code=1)
    except FileNotFoundError as e:
        click.echo(f"File not found: {e.filename} {e.strerror}", err=True)
        raise Exit(code=1)
    except ValidationError as e:
        click.echo(f"Validation failed for Config file: {e.json()}", err=True)
        raise Exit(code=1)
    except UnexpectedResponse as e:
        click.echo(f"Failed to update project {id}: {e.status_code} {e.content}", err=True)
        raise Exit(code=1)
