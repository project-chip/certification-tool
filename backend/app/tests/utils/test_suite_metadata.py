from typing import Any, Dict, Optional

from faker import Faker
from sqlalchemy.orm import Session

from app.models import TestSuiteMetadata
from app.tests.utils.utils import random_test_public_id

fake = Faker()


def random_test_suite_metadata_dict(
    public_id: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    version: Optional[str] = None,
    source_hash: Optional[str] = None,
    source_location: Optional[str] = None,
) -> Dict[str, Any]:
    if public_id is None:
        public_id = random_test_public_id()
    if title is None:
        title = fake.text(max_nb_chars=20)
    if description is None:
        description = fake.text(max_nb_chars=200)
    if version is None:
        version = fake.bothify(text="#.##.##")
    if source_hash is None:
        source_hash = fake.sha256(raw_output=False)

    return {
        "public_id": public_id,
        "title": title,
        "description": description,
        "version": version,
        "source_hash": source_hash,
    }


def create_random_test_suite_metadata(db: Session, **kwargs: Any) -> TestSuiteMetadata:
    test_suite_metadata = TestSuiteMetadata(**random_test_suite_metadata_dict(**kwargs))
    db.add(test_suite_metadata)
    db.commit()
    return test_suite_metadata
