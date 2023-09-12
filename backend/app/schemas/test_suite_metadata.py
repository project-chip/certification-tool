from datetime import datetime

from pydantic import BaseModel


# Shared properties
class TestSuiteMetadataBase(BaseModel):
    __test__ = False  # Needed to indicate to PyTest that this is not a "test"
    public_id: str
    title: str
    description: str
    version: str
    source_hash: str

    class Config:
        orm_mode = True


# Properties shared by models stored in DB
class TestSuiteMetadataInDBBase(TestSuiteMetadataBase):
    id: int


# Properties to return to client
class TestSuiteMetadata(TestSuiteMetadataInDBBase):
    pass


# Additional Properties properties stored in DB
class TestSuiteMetadataInDB(TestSuiteMetadataInDBBase):
    created_at: datetime
