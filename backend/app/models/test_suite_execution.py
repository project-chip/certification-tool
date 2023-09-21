from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ARRAY, Enum, ForeignKey, String, func, select
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

from .test_case_execution import TestCaseExecution
from .test_enums import TestStateEnum

if TYPE_CHECKING:
    from .test_run_execution import TestRunExecution  # noqa: F401
    from .test_suite_metadata import TestSuiteMetadata  # noqa: F401


class TestSuiteExecution(Base):
    __test__ = False  # Needed to indicate to PyTest that this is not a "test"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    public_id: Mapped[str] = mapped_column(nullable=False)
    execution_index: Mapped[int] = mapped_column(nullable=False)

    state: Mapped[TestStateEnum] = mapped_column(
        Enum(TestStateEnum), nullable=False, default=TestStateEnum.PENDING
    )

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    started_at: Mapped[Optional[datetime]]
    completed_at: Mapped[Optional[datetime]]

    errors: Mapped[list[str]] = mapped_column(
        ARRAY(String, dimensions=1), nullable=False, default=[]
    )

    test_suite_metadata_id: Mapped[int] = mapped_column(
        ForeignKey("testsuitemetadata.id"), nullable=False
    )
    test_suite_metadata: Mapped["TestSuiteMetadata"] = relationship(
        "TestSuiteMetadata", back_populates="test_suite_executions"
    )

    test_run_execution_id: Mapped[int] = mapped_column(
        ForeignKey("testrunexecution.id"), nullable=False
    )
    test_run_execution: Mapped["TestRunExecution"] = relationship(
        "TestRunExecution", back_populates="test_suite_executions"
    )

    test_case_executions: Mapped[list["TestCaseExecution"]] = relationship(
        TestCaseExecution,
        back_populates="test_suite_execution",
        uselist=True,
        order_by="TestCaseExecution.execution_index",
        collection_class=ordering_list("execution_index"),
        cascade="all, delete-orphan",
    )

    @hybrid_property
    def test_case_execution_count(self) -> int:
        return (
            self.obj_session().scalar(
                select(func.count())
                .select_from(TestCaseExecution)
                .filter(TestCaseExecution.test_suite_execution == self)
            )
            or 0
        )
