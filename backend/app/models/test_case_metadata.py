from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import VARCHAR, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .test_case_execution import TestCaseExecution  # noqa: F401


class TestCaseMetadata(Base):
    __test__ = False  # Needed to indicate to PyTest that this is not a "test"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    public_id: Mapped[str] = mapped_column(nullable=False)

    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str] = mapped_column(nullable=False)
    source_hash: Mapped[str] = mapped_column(VARCHAR(64), nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)

    test_case_executions: Mapped[list["TestCaseExecution"]] = relationship(
        "TestCaseExecution", back_populates="test_case_metadata", uselist=True
    )
