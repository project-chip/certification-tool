from .base import CRUDOperationNotSupported
from .crud_operator import operator
from .crud_project import project
from .crud_test_case_execution import test_case_execution
from .crud_test_case_metadata import test_case_metadata
from .crud_test_run_config import test_run_config
from .crud_test_run_execution import test_run_execution
from .crud_test_step_execution import test_step_execution
from .crud_test_suite_execution import test_suite_execution
from .crud_test_suite_metadata import test_suite_metadata

# For a new basic set of CRUD operations you could just do

# from .base import CRUDBase
# from app.models.item import Item
# from app.schemas.item import ItemCreate, ItemUpdate

# item = CRUDBase[Item, ItemCreate, ItemUpdate](Item)
