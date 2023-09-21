from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OperatorBase(BaseModel):
    """Base schema for Operator, with shared properties."""

    name: Optional[str]


class OperatorCreate(OperatorBase):
    """Create schema.

    Name is required for new Operators.
    """

    name: str


class OperatorUpdate(OperatorBase):
    """Update Schema.

    Same as the base schema, only name can be changed"""


class OperatorInDBBase(OperatorBase):
    """Base schema for operator in DB.

    Id, and name are required fields.
    """

    id: int
    name: str

    class Config:
        """Configure DB schemas to support parsing from ORM models."""

        orm_mode = True


class Operator(OperatorInDBBase):
    """Default schema, used when return data to API clients"""


class OperatorInDB(OperatorInDBBase):
    """Full database schema.

    Has internal fields for tracking model changes.
    """

    created_at: datetime
    updated_at: datetime


class OperatorToExport(OperatorBase):
    name: str

    class Config:
        """Configure DB schemas to support parsing from ORM models."""

        orm_mode = True
