import pytest

from app.test_engine.test_script_manager import (
    TestCaseNotFound,
    TestCollectionNotFound,
    TestSuiteNotFound,
    test_script_manager,
)


@pytest.mark.asyncio
async def test_validate_test_selection_OK() -> None:
    selected_tests = {
        "tool_unit_tests": {
            "TestSuiteExpected": {"TCTRExpectedPass": 1},
            "TestSuiteAsync": {"TCTRInstantPass": 1, "TCTRNeverEnding": 3},
        },
        "sample_tests": {"SampleTestSuite1": {"TCSS1001": 1}},
    }

    test_script_manager.validate_test_selection(selected_tests)


@pytest.mark.asyncio
async def test_validate_test_selection_invalid_test_collection() -> None:
    selected_tests = {
        "tool_unit_tests": {
            "TestSuiteExpected": {"TCTRExpectedPass": 1},
            "TestSuiteAsync": {"TCTRInstantPass": 1, "TCTRNeverEnding": 3},
        },
        # Following test collection does not exist
        "invalid_name": {
            "TestSuiteExpected": {"TCTRExpectedPass": 1},
        },
    }
    with pytest.raises(TestCollectionNotFound):
        test_script_manager.validate_test_selection(selected_tests)


@pytest.mark.asyncio
async def test_validate_test_selection_invalid_test_suite() -> None:
    # Test non existing test
    selected_tests = {
        "tool_unit_tests": {
            "TestSuiteExpected": {"TCTRExpectedPass": 1},
            # Following test suite does not exist
            "invalid_test_suite": {"TCTRExpectedPass": 1},
        }
    }
    with pytest.raises(TestSuiteNotFound):
        test_script_manager.validate_test_selection(selected_tests)

    # Test existing test suite from other collection
    selected_tests = {
        "tool_unit_tests": {
            "TestSuiteExpected": {"TCTRExpectedPass": 1},
            "TestSuiteAsync": {"TCTRInstantPass": 1, "TCTRNeverEnding": 3},
        },
        "sample_tests": {
            # Following test suite is not in this collection
            "TestSuiteExpected": {"TCTRExpectedPass": 1},
        },
    }
    with pytest.raises(TestSuiteNotFound):
        test_script_manager.validate_test_selection(selected_tests)


@pytest.mark.asyncio
async def test_validate_test_selection_invalid_test_case() -> None:
    # Test non existing test
    selected_tests = {
        "tool_unit_tests": {
            "TestSuiteExpected": {
                "TCTRExpectedPass": 1,
                # Following test case does not exist
                "invalid_test_case": 1,
            },
        }
    }
    with pytest.raises(TestCaseNotFound):
        test_script_manager.validate_test_selection(selected_tests)

    # Test existing test case from other test suite
    selected_tests = {
        "tool_unit_tests": {
            "TestSuiteAsync": {
                "TCTRInstantPass": 1,
                "TCTRNeverEnding": 3,
                # Following test case is not in this collection
                "TCTRExpectedPass": 1,
            },
        }
    }
    with pytest.raises(TestCaseNotFound):
        test_script_manager.validate_test_selection(selected_tests)
