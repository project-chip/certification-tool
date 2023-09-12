from sqlalchemy.orm import Session

from app import crud
from app.models import TestCaseExecution
from app.tests.utils.test_case_execution import random_test_case_execution_dict
from app.tests.utils.test_case_metadata import create_random_test_case_metadata
from app.tests.utils.test_suite_execution import create_random_test_suite_execution


def test_get_test_case_execution(db: Session) -> None:
    # Create required relations for test_case_execution
    test_case_metadata = create_random_test_case_metadata(db)
    test_suite_execution = create_random_test_suite_execution(db)

    # Create build new test_case_execution object
    test_case_execution_dict = random_test_case_execution_dict(
        public_id=test_case_metadata.public_id,
        test_case_metadata_id=test_case_metadata.id,
        test_suite_execution_id=test_suite_execution.id,
    )
    test_case_execution = TestCaseExecution(**test_case_execution_dict)

    # Save test_case_execution in DB
    test_suite_execution.test_case_executions.append(test_case_execution)
    db.commit()

    # Load stored test_case_execution form DB
    stored_test_case_execution = crud.test_case_execution.get(
        db=db, id=test_case_execution.id
    )

    # assert created db values match
    assert stored_test_case_execution is not None
    assert stored_test_case_execution.public_id == test_case_metadata.public_id

    # assert relations
    assert stored_test_case_execution.test_case_metadata.id == test_case_metadata.id
    assert stored_test_case_execution.test_suite_execution.id == test_suite_execution.id
