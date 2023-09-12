from fastapi import APIRouter

from app import schemas
from app.schemas.test_harness_backend_version import TestHarnessBackendVersion
from app.version import version_information

router = APIRouter()


@router.get(
    "/version",
    response_model=schemas.TestHarnessBackendVersion,
    response_model_exclude_none=True,
)
def get_test_harness_backend_version() -> TestHarnessBackendVersion:
    """
    Retrieve version of the Test Engine.

    """
    return version_information
