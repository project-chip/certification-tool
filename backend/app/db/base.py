# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.operator import Operator  # noqa
from app.models.project import Project  # noqa
from app.models.test_case_execution import TestCaseExecution  # noqa
from app.models.test_case_metadata import TestCaseMetadata  # noqa
from app.models.test_run_config import TestRunConfig  # noqa
from app.models.test_run_execution import TestRunExecution  # noqa
from app.models.test_step_execution import TestStepExecution  # noqa
from app.models.test_suite_execution import TestSuiteExecution  # noqa
from app.models.test_suite_metadata import TestSuiteMetadata  # noqa
