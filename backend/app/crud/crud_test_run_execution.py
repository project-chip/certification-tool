from datetime import datetime
from typing import List, Optional, Sequence

from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.crud import operator as crud_operator
from app.crud import project as crud_project
from app.crud import test_run_config as crud_test_run_config
from app.crud.base import CRUDBaseCreate, CRUDBaseDelete, CRUDBaseRead
from app.models import Project, TestCaseExecution, TestRunExecution, TestSuiteExecution
from app.schemas import (
    TestRunConfigCreate,
    TestRunExecutionToExport,
    TestRunExecutionToImport,
)
from app.schemas.operator import Operator
from app.schemas.test_run_config import TestRunConfigInDB
from app.schemas.test_run_execution import (
    TestRunExecutionCreate,
    TestRunExecutionStats,
    TestRunExecutionWithStats,
)
from app.schemas.test_selection import TestSelection
from app.test_engine.test_script_manager import test_script_manager


class ImportError(Exception):
    """
    Exception raised for errors while importing 'Test Run Execution
    """


class CRUDTestRunExecution(
    CRUDBaseRead[TestRunExecution],
    CRUDBaseDelete[TestRunExecution],
    CRUDBaseCreate[TestRunExecution, TestRunExecutionCreate],
):
    def get_multi(
        self,
        db: Session,
        *,
        project_id: Optional[int] = None,
        archived: Optional[bool] = False,
        search_query: Optional[str] = None,
        order_by: Optional[str] = None,
        skip: Optional[int] = 0,
        limit: Optional[int] = 100,
    ) -> Sequence[TestRunExecution]:
        query = self.select()

        if project_id is not None:
            query = query.filter(self.model.project_id == project_id)

        if archived:
            query = query.filter(self.model.archived_at.isnot(None))
        else:
            query = query.filter(self.model.archived_at.is_(None))

        if search_query is not None:
            like_filter = f"%{search_query}%"
            query = query.filter(
                or_(
                    self.model.title.ilike(like_filter),
                    self.model.description.ilike(like_filter),
                )
            )

        if order_by is None:
            query = query.order_by(self.model.id)
        else:
            query = query.order_by(order_by)

        query = query.offset(skip).limit(limit)

        return db.scalars(query).all()

    def get_multi_with_stats(
        self,
        db: Session,
        *,
        project_id: Optional[int] = None,
        archived: Optional[bool] = False,
        search_query: Optional[str] = None,
        order_by: Optional[str] = None,
        skip: Optional[int] = 0,
        limit: Optional[int] = 100,
    ) -> List[TestRunExecutionWithStats]:
        results = self.get_multi(
            db=db,
            project_id=project_id,
            archived=archived,
            search_query=search_query,
            order_by=order_by,
            skip=skip,
            limit=limit,
        )
        # load stats for each test run
        return list(map(lambda tre: self.__load_stats(db, tre), results))

    def __load_stats(
        self, db: Session, test_run_execution: TestRunExecution
    ) -> TestRunExecutionWithStats:
        stats = TestRunExecutionStats()

        # get total test case count
        count = (
            db.scalar(
                select(func.count())
                .select_from(TestCaseExecution)
                .join(TestSuiteExecution)
                .join(TestRunExecution)
                .filter(TestRunExecution.id == test_run_execution.id)
            )
            or 0
        )

        stats.test_case_count = count

        # Collect state statistics
        state_counts = db.execute(
            select(func.count(TestCaseExecution.state), TestCaseExecution.state)
            .join(TestSuiteExecution)
            .join(TestRunExecution)
            .filter(TestRunExecution.id == test_run_execution.id)
            .group_by(TestCaseExecution.state)
        ).all()
        # The state counts are returned as a list of tuples (Count, Enum):
        # Example: [(11, TestStateEnum.ERROR), (1, TestStateEnum.PENDING)]
        # Below we extract these stats, and use subscript notation to access
        # the tuple elements
        for state_count in state_counts:
            count = state_count[0]
            state = state_count[1].value
            stats.states[state] = count

        result = TestRunExecutionWithStats(
            **dict(test_run_execution.__dict__, test_case_stats=stats)
        )

        # Operator is lazy loaded, so it might not be included in __dict__.
        # TODO #296: This could be solved by using from_orm, but it doesn't
        # support adding the `test_case_stats` see :
        # https://github.com/samuelcolvin/pydantic/pull/3375
        #
        if test_run_execution.operator is not None:
            result.operator = Operator.from_orm(test_run_execution.operator)

        return result

    def create(
        self,
        db: Session,
        obj_in: TestRunExecutionCreate,
        **kwargs: Optional[dict],
    ) -> TestRunExecution:
        # TODO(#123): Remove "auto first project" when UI supports project management.
        # This will ensure that a test_run_execution is always associated with a project
        if obj_in.project_id is None:
            project = self.find_or_create_first_project(db)
            obj_in.project_id = project.id

        test_run_execution = super().create(db=db, obj_in=obj_in)

        # https://github.com/chip-csg/chip-certification-tool-backend/issues/103
        # TODO: while we change the API. selected tests can come from two places:
        # 1. Pass in directly
        # 2. from the optional test_run_config
        selected_tests: Optional[TestSelection] = kwargs.get("selected_tests")

        if selected_tests is None:
            # We use the Pydantic schema to deserialize the selected_tests json column
            selected_tests = TestRunConfigInDB.from_orm(
                test_run_execution.test_run_config
            ).selected_tests

        test_suites = (
            test_script_manager.pending_test_suite_executions_for_selected_tests(
                selected_tests
            )
        )

        test_run_execution.test_suite_executions.extend(test_suites)

        db.commit()
        db.refresh(test_run_execution)
        return test_run_execution

    # TODO(#123): Remove "auto first project" when UI supports project management.
    def find_or_create_first_project(self, db: Session) -> Project:
        """Get a project. Create one if none exists.

        Args:
            db (Session): used to find the project.

        Returns:
            Project: first found project, or a newly created project.
        """

        project = db.scalar(select(Project).limit(1))

        if project is None:
            project = Project(name="First Project")
            db.add(project)
            db.commit()
            db.refresh(project)

        return project

    def archive(self, db: Session, db_obj: TestRunExecution) -> TestRunExecution:
        db_obj.archived_at = datetime.now()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def unarchive(self, db: Session, db_obj: TestRunExecution) -> TestRunExecution:
        db_obj.archived_at = None
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def import_execution(
        self,
        db: Session,
        project_id: int,
        execution: TestRunExecutionToExport,
    ) -> TestRunExecution:
        """
        Import a test run execution into the database.

        Args:
            db (Session): The database session
            project_id (int): ID of the project that will have the imported
            execution (TestRunExecutionToExport): Information about the test run
            execution exported

        Raises:
            ImportError: If the project_id is invalid

        Returns:
            TestRunExecution: The test run execution object that has been added to the
            database
        """
        if crud_project.get(db=db, id=project_id) is None:
            raise ImportError(f"Project with id {project_id} not found")

        imported_execution = TestRunExecutionToImport(
            project_id=project_id, imported_at=datetime.now(), **execution.__dict__
        )

        if operator := execution.operator:
            operator_id = crud_operator.get_or_create(
                db=db, name=operator.name, commit=False
            )
            imported_execution.operator_id = operator_id

        if execution.test_run_config:
            test_run_config = crud_test_run_config.create(
                db=db, obj_in=TestRunConfigCreate(**execution.test_run_config.__dict__)
            )
            imported_execution.test_run_config_id = test_run_config.id

        imported_model = TestRunExecution(**jsonable_encoder(imported_execution))

        db.add(imported_model)
        db.commit()
        db.refresh(imported_model)

        return imported_model


test_run_execution = CRUDTestRunExecution(TestRunExecution)
