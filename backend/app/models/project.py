from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.db.pydantic_data_type import PydanticModelType
from app.schemas.pics import PICS
from app.schemas.test_environment_config import TestEnvironmentConfig

if TYPE_CHECKING:
    from .test_run_execution import TestRunExecution  # noqa: F401


class Project(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)

    config: Mapped[TestEnvironmentConfig] = mapped_column(
        PydanticModelType(TestEnvironmentConfig),
        nullable=False,
    )

    pics: Mapped[PICS] = mapped_column(
        PydanticModelType(PICS), default=PICS(), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    archived_at: Mapped[Optional[datetime]] = mapped_column(default=None, nullable=True)

    test_run_executions: Mapped[list["TestRunExecution"]] = relationship(
        "TestRunExecution",
        back_populates="project",
        uselist=True,
        cascade="all, delete-orphan",
    )
