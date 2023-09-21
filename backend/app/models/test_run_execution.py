from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Enum, ForeignKey, func, select
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import Mapped, mapped_column, relationship, with_parent

from app.db.base_class import Base
from app.db.pydantic_data_type import PydanticListType

from .test_enums import TestStateEnum
from .test_suite_execution import TestSuiteExecution

if TYPE_CHECKING:
    from .operator import Operator  # noqa: F401
    from .project import Project  # noqa: F401
    from .test_run_config import TestRunConfig  # noqa: F401


class TestRunExecution(Base):
    # Import pydantic schema here to avoid circular import issues
    from app.schemas.test_run_log_entry import TestRunLogEntry

    __test__ = False  # Needed to indicate to PyTest that this is not a "test"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    state: Mapped[TestStateEnum] = mapped_column(
        Enum(TestStateEnum), nullable=False, default=TestStateEnum.PENDING
    )
    title: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    started_at: Mapped[Optional[datetime]]
    completed_at: Mapped[Optional[datetime]]
    archived_at: Mapped[Optional[datetime]]
    imported_at: Mapped[Optional[datetime]]

    description: Mapped[Optional[str]] = mapped_column(default=None, nullable=True)

    test_run_config_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("testrunconfig.id"), nullable=True
    )
    test_run_config: Mapped["TestRunConfig"] = relationship(
        "TestRunConfig", back_populates="test_run_executions"
    )
    log: Mapped[list[TestRunLogEntry]] = mapped_column(
        MutableList.as_mutable(PydanticListType(TestRunLogEntry)),
        default=[],
        nullable=False,
    )

    test_suite_executions: Mapped[list["TestSuiteExecution"]] = relationship(
        TestSuiteExecution,
        back_populates="test_run_execution",
        uselist=True,
        order_by="TestSuiteExecution.execution_index",
        collection_class=ordering_list("execution_index"),
        cascade="all, delete-orphan",
    )
    operator_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("operator.id"), nullable=True
    )
    operator: Mapped["Operator"] = relationship(
        "Operator", back_populates="test_run_executions"
    )
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=False)
    project: Mapped["Project"] = relationship(
        "Project", back_populates="test_run_executions"
    )

    def append_to_log(self, log_record: "TestRunLogEntry") -> None:
        self.log.append(log_record)

    def test_suite_execution_by_public_id(
        self, public_id: str
    ) -> Optional[TestSuiteExecution]:
        return self.obj_session().scalar(
            select(TestSuiteExecution)
            .where(with_parent(self, TestSuiteExecution.test_run_execution))
            .filter_by(public_id=public_id)
            .limit(1)
        )

    @hybrid_property
    def test_suite_execution_count(self) -> int:
        return (
            self.obj_session().scalar(
                select(func.count())
                .select_from(TestSuiteExecution)
                .filter(TestSuiteExecution.test_run_execution == self)
            )
            or 0
        )
