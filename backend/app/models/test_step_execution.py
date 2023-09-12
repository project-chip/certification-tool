from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ARRAY, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

from .test_enums import TestStateEnum

if TYPE_CHECKING:
    from .test_case_execution import TestCaseExecution  # noqa: F401


class TestStepExecution(Base):
    __test__ = False  # Needed to indicate to PyTest that this is not a "test"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(nullable=False)
    execution_index: Mapped[int] = mapped_column(nullable=False)

    state: Mapped[TestStateEnum] = mapped_column(
        Enum(TestStateEnum), nullable=False, default=TestStateEnum.PENDING
    )

    errors: Mapped[list[str]] = mapped_column(
        ARRAY(String, dimensions=1), nullable=False, default=[]
    )
    failures: Mapped[list[str]] = mapped_column(
        ARRAY(String, dimensions=1), nullable=False, default=[]
    )

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    started_at: Mapped[Optional[datetime]]
    completed_at: Mapped[Optional[datetime]]

    test_case_execution_id: Mapped[int] = mapped_column(
        ForeignKey("testcaseexecution.id"), nullable=False
    )
    test_case_execution: Mapped["TestCaseExecution"] = relationship(
        "TestCaseExecution", back_populates="test_step_executions"
    )
