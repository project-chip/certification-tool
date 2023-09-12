from pydantic import BaseModel


# Shared properties
class TestHarnessBackendVersion(BaseModel):
    version: str
    sha: str
    sdk_sha: str
    db_revision: str
