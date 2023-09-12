from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .test_run_execution import TestRunExecution  # noqa: F401


class TestRunConfig(Base):
    __test__ = False  # Needed to indicate to PyTest that this is not a "test"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    dut_name: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    selected_tests: Mapped[dict] = mapped_column(JSON, default={}, nullable=False)

    test_run_executions: Mapped[list["TestRunExecution"]] = relationship(
        "TestRunExecution", back_populates="test_run_config", uselist=True
    )
