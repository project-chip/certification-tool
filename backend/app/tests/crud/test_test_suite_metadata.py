from sqlalchemy.orm import Session

from app import crud
from app.models import TestSuiteMetadata
from app.tests.utils.test_suite_metadata import random_test_suite_metadata_dict
from app.tests.utils.utils import random_lower_string


def test_get_test_suite_metadata(db: Session) -> None:
    # Create build new test_suite_metadata object
    title = random_lower_string()
    description = random_lower_string()
    test_suite_metadata_dict = random_test_suite_metadata_dict(
        title=title, description=description
    )
    test_suite_metadata = TestSuiteMetadata(**test_suite_metadata_dict)

    # Save create test_suite_metadata in DB
    db.add(test_suite_metadata)
    db.commit()

    # load stored test_suite_metadata from DB
    stored_test_suite_metadata = crud.test_suite_metadata.get(
        db=db, id=test_suite_metadata.id
    )

    # assert stored values match
    assert stored_test_suite_metadata
    assert test_suite_metadata.id == stored_test_suite_metadata.id
    assert test_suite_metadata.title == stored_test_suite_metadata.title
    assert test_suite_metadata.description == stored_test_suite_metadata.description
