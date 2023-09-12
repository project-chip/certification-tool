from sqlalchemy.orm import Session

from app import crud
from app.models import TestCaseMetadata
from app.tests.utils.test_case_metadata import random_test_case_metadata_dict
from app.tests.utils.utils import random_lower_string


def test_get_test_case_metadata(db: Session) -> None:
    # Create build new test_case_metadata object
    title = random_lower_string()
    description = random_lower_string()
    test_case_metadata_dict = random_test_case_metadata_dict(
        title=title, description=description
    )
    test_case_metadata = TestCaseMetadata(**test_case_metadata_dict)

    # Save create test_case_metadata in DB
    db.add(test_case_metadata)
    db.commit()

    # load stored test_case_metadata from DB
    stored_test_case_metadata = crud.test_case_metadata.get(
        db=db, id=test_case_metadata.id
    )

    # assert stored values match
    assert stored_test_case_metadata
    assert test_case_metadata.id == stored_test_case_metadata.id
    assert test_case_metadata.title == stored_test_case_metadata.title
    assert test_case_metadata.description == stored_test_case_metadata.description
