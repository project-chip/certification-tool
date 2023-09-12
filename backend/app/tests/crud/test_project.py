from sqlalchemy.orm import Session

from app import crud
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.tests.utils.project import (
    create_random_project,
    create_random_project_archived,
)
from app.tests.utils.test_run_execution import create_random_test_run_execution
from app.tests.utils.utils import random_lower_string


def test_create_project(db: Session) -> None:
    name = random_lower_string()
    wifi_ssid = random_lower_string()
    project_in = ProjectCreate(name=name, wifi_ssid=wifi_ssid)
    project = crud.project.create(db=db, obj_in=project_in)
    assert project.name == name


def test_get_project(db: Session) -> None:
    project = create_random_project(db=db)

    stored_project = crud.project.get(db=db, id=project.id)
    assert stored_project
    assert project.id == stored_project.id
    assert project.name == stored_project.name


def test_project_archive(db: Session) -> None:
    project = create_random_project(db=db)
    assert project.archived_at is None

    archived_project = crud.project.archive(db=db, db_obj=project)

    assert archived_project
    assert archived_project.archived_at is not None


def test_project_unarchive(db: Session) -> None:
    archived_project = create_random_project_archived(db)

    assert archived_project
    assert archived_project.archived_at is not None

    unarchived_project = crud.project.unarchive(db=db, db_obj=archived_project)

    assert unarchived_project
    assert unarchived_project.archived_at is None


def test_get_multi_project(db: Session) -> None:
    project1 = create_random_project(db)
    project2 = create_random_project(db)
    project_archived = create_random_project_archived(db)

    # disable skip and limit, do disable default pagination
    projects = crud.project.get_multi(db=db, skip=None, limit=None)
    assert projects

    # project_archived shouldn't be in the list
    assert any(p.id == project1.id for p in projects)
    assert any(p.id == project2.id for p in projects)
    assert not any(p.id == project_archived.id for p in projects)


def test_get_multi_project_archived(db: Session) -> None:
    project1 = create_random_project_archived(db)
    project2 = create_random_project_archived(db)
    project_not_archived = create_random_project(db)

    # disable skip and limit, do disable default pagination
    projects = crud.project.get_multi(db=db, archived=True, skip=None, limit=None)

    # project_not_archived shouldn't be in the list
    assert any(p.id == project1.id for p in projects)
    assert any(p.id == project2.id for p in projects)
    assert not any(p.id == project_not_archived.id for p in projects)


def test_update_project(db: Session) -> None:
    project = create_random_project(db=db)

    new_name = random_lower_string()
    project_update = ProjectUpdate(name=new_name)

    updated_project = crud.project.update(db=db, db_obj=project, obj_in=project_update)

    assert project.id == updated_project.id

    assert updated_project.name == new_name


def test_delete_project(db: Session) -> None:
    project = create_random_project(db=db)

    project2 = crud.project.remove(db=db, id=project.id)
    assert project2 is not None
    assert project2.id == project.id
    assert project2.name == project.name

    project3 = crud.project.get(db=db, id=project.id)
    assert project3 is None


def test_delete_project_with_nested_test_run(db: Session) -> None:
    test_run = create_random_test_run_execution(db)
    project = test_run.project

    # Make sure DB session doesn't reuse models
    db.expunge(project)

    project2 = crud.project.remove(db=db, id=project.id)
    assert project2 is not None
    assert project2.id == project.id
    assert project2.name == project.name

    project3 = crud.project.get(db=db, id=project.id)
    assert project3 is None

    # Verify that the nested test_run is deleted.
    test_run2 = crud.test_run_execution.get(db=db, id=test_run.id)
    assert test_run2 is None
