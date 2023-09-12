from typing import Any
from unittest import mock
from unittest.mock import MagicMock, PropertyMock

from app.default_environment_config import default_environment_config
from app.models import TestCaseExecution
from app.test_engine.models.test_case import TestCase

TEST_PARAMETER_NAME_1 = "param1"
TEST_PARAMETER_NAME_2 = "param2"
TEST_PARAMETER_NAME_3 = "param3"

DEFAULT_TEST_PARAMETERS = {TEST_PARAMETER_NAME_1: 1, TEST_PARAMETER_NAME_2: "two"}


class SomeTestParamsTestCase(TestCase):
    @classmethod
    def default_test_parameters(cls) -> dict[str, Any]:
        return DEFAULT_TEST_PARAMETERS

    def create_test_steps(self) -> None:
        # Method must be implemented in TestCase subclass
        return


class NoDefaultTestParamsTestCase(TestCase):
    def create_test_steps(self) -> None:
        # Method must be implemented in TestCase subclass
        return


def test_test_case_test_params_merged() -> None:
    """Test that a TestCase default test parameters and runtime config test parameters
    are merged.
    """
    # Mock config
    mock_config = default_environment_config.copy(deep=True)
    mock_config.test_parameters = {
        TEST_PARAMETER_NAME_1: 11,
        TEST_PARAMETER_NAME_3: 333,
    }

    with mock.patch(
        "app.test_engine.models.test_case.TestCase.config",
        new_callable=PropertyMock,
        return_value=mock_config,
    ) as _:
        case = SomeTestParamsTestCase(
            test_case_execution=MagicMock(spec=TestCaseExecution)
        )
        # Assert parameter 1 is updated from config
        assert TEST_PARAMETER_NAME_1 in case.test_parameters
        assert case.test_parameters[TEST_PARAMETER_NAME_1] == 11

        # Assert parameter 2 is present and default
        assert TEST_PARAMETER_NAME_2 in case.test_parameters
        assert (
            case.test_parameters[TEST_PARAMETER_NAME_2]
            == DEFAULT_TEST_PARAMETERS[TEST_PARAMETER_NAME_2]
        )

        # Assert parameter 3 is NOT present as it is not in default test parameters
        assert TEST_PARAMETER_NAME_3 not in case.test_parameters


def test_test_case_no_test_parameters() -> None:
    """Test that a TestCase without default test parameters will not have runtime test
    parameters.
    """
    mock_config = default_environment_config.copy(deep=True)
    mock_config.test_parameters = {
        TEST_PARAMETER_NAME_1: 11,
        TEST_PARAMETER_NAME_3: 333,
    }

    with mock.patch(
        "app.test_engine.models.test_case.TestCase.config",
        new_callable=PropertyMock,
        return_value=mock_config,
    ) as _:
        case = NoDefaultTestParamsTestCase(
            test_case_execution=MagicMock(spec=TestCaseExecution)
        )
        assert case.test_parameters == {}
