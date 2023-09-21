from datetime import datetime
from typing import Any, Dict, Optional

from faker import Faker
from sqlalchemy.orm import Session

from app import crud, models
from app.models import TestRunExecution
from app.models.test_enums import TestStateEnum
from app.schemas import TestSelection
from app.schemas.test_run_execution import TestRunExecutionCreate
from app.tests.utils.project import create_random_project

fake = Faker()


def random_test_run_execution_dict(
    state: Optional[TestStateEnum] = None,
    title: Optional[str] = None,
    started_at: Optional[datetime] = None,
    completed_at: Optional[datetime] = None,
    project_id: Optional[int] = None,
    operator_id: Optional[int] = None,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    output: Dict[str, Any] = {}

    # State is optional, include if present
    if state is not None:
        output["state"] = state

    # Title is not optional,
    if title is None:
        title = fake.text(max_nb_chars=20)
    output["title"] = title

    # Started At is optional, include if present
    if started_at is not None:
        output["started_at"] = started_at

    # Completed At is optional, include if present
    if completed_at is not None:
        output["completed_at"] = completed_at

    # project_id is optional, include if present
    if project_id is not None:
        output["project_id"] = project_id

    # operator_id is optional, include if present
    if operator_id is not None:
        output["operator_id"] = operator_id

    # description is optional, include if present
    if description is not None:
        output["description"] = description

    return output


def create_random_test_run_execution_archived(
    db: Session, **kwargs: Any
) -> models.TestRunExecution:
    run = create_random_test_run_execution(db=db, **kwargs)
    return crud.test_run_execution.archive(db=db, db_obj=run)


def create_random_test_run_execution(
    db: Session, selected_tests: Optional[TestSelection] = {}, **kwargs: Any
) -> models.TestRunExecution:
    test_run_execution_dict = random_test_run_execution_dict(**kwargs)

    if test_run_execution_dict.get("project_id") is None:
        project = create_random_project(db)
        test_run_execution_dict["project_id"] = project.id

    test_run_execution_in = TestRunExecutionCreate(**test_run_execution_dict)
    return crud.test_run_execution.create(
        db=db, obj_in=test_run_execution_in, selected_tests=selected_tests
    )


def create_random_test_run_execution_with_test_case_states(
    db: Session, test_case_states: Dict[TestStateEnum, int]
) -> models.TestRunExecution:
    # As we need to control the number of test_case statuses, we need to create a fake
    # run config with the same amount of test cases. We have to use a "real" test suite
    # and real test case
    num_test_cases = sum(test_case_states.values())
    selected_tests: dict = {
        "sample_tests": {"SampleTestSuite1": {"TCSS1001": num_test_cases}}
    }
    test_run_execution = create_random_test_run_execution(
        db=db, selected_tests=selected_tests
    )

    test_suite_execution = test_run_execution.test_suite_executions[0]
    test_case_executions = test_suite_execution.test_case_executions
    # set test_cases statuses
    test_case_idx = 0
    for state, count in test_case_states.items():
        for i in range(count):
            test_case_execution = test_case_executions[test_case_idx]
            test_case_execution.state = state
            test_case_idx += 1
    db.commit()

    return test_run_execution


def create_test_run_execution_with_some_test_cases(
    db: Session, **kwargs: Any
) -> TestRunExecution:
    return create_random_test_run_execution(
        db=db,
        selected_tests={
            "sample_tests": {
                "SampleTestSuite1": {"TCSS1001": 1, "TCSS1002": 2, "TCSS1003": 3}
            }
        },
        **kwargs
    )


test_run_execution_base_dict = {
    "title": "UI_Test_Run_2023_05_23_18_43_30",
    "description": "",
    "state": "passed",
    "started_at": "2023-05-23T21:43:43.543147",
    "completed_at": "2023-05-23T23:34:39.232447",
    "imported_at": None,
    "archived_at": None,
    "created_at": "2023-05-23T21:43:31.038050",
    "log": [
        {
            "level": "INFO",
            "timestamp": 1684878223.482982,
            "message": "Run Test Runner is Ready",
            "test_suite_execution_index": None,
            "test_case_execution_index": None,
            "test_step_execution_index": None,
        },
    ],
    "test_suite_executions": [
        {
            "state": "passed",
            "public_id": "FirstChipToolSuite",
            "started_at": "2023-05-23T21:43:43.629123",
            "completed_at": "2023-05-23T23:34:39.155045",
            "errors": [],
            "created_at": "2023-05-23T21:43:31.395973",
            "test_suite_metadata": {
                "public_id": "FirstChipToolSuite",
                "title": "FirstChipToolSuite",
                "description": "FirstChipToolSuite",
                "version": "0.0.1",
                "source_hash": "de7f3c1390cd283f91f74a334aaf0ec3",
            },
            "execution_index": 0,
            "test_case_executions": [
                {
                    "state": "passed",
                    "public_id": "TC-ACE-1.1",
                    "started_at": "2023-05-23T21:44:02.381832",
                    "completed_at": "2023-05-23T21:44:28.937346",
                    "errors": [],
                    "created_at": "2023-05-23T21:43:31.451550",
                    "test_case_metadata": {
                        "public_id": "TC-ACE-1.1",
                        "title": "TC-ACE-1.1",
                        "description": "42.1.1. [TC-ACE-1.1] Privileges",
                        "version": "0.0.1",
                        "source_hash": "de7f3c1390cd283f91f74a334aaf0ec3",
                    },
                    "execution_index": 0,
                    "test_step_executions": [
                        {
                            "state": "passed",
                            "title": "Start chip-tool test",
                            "started_at": "2023-05-23T21:44:02.472236",
                            "completed_at": "2023-05-23T21:44:09.586133",
                            "errors": [],
                            "failures": [],
                            "created_at": "2023-05-23T21:43:32.764343",
                            "execution_index": 0,
                        },
                    ],
                }
            ],
        }
    ],
}
