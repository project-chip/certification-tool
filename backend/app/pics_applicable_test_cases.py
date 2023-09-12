from loguru import logger

from app.schemas.pics import PICS, PICSApplicableTestCases
from app.test_engine.test_script_manager import test_script_manager


def applicable_test_cases_list(pics: PICS) -> PICSApplicableTestCases:
    """Returns the applicable test cases for this project given the set of PICS"

    Args:
        pics (PICS): set of pics to map against

    Returns:
        PICSApplicableTestCases: List of test cases that are applicable
          for this Project
    """
    applicable_tests: set = set()

    if len(pics.clusters) == 0:
        # If the user has not uploaded any PICS
        # i.e, there are no PICS associated with the project then return empty set
        logger.debug(f"Applicable test cases: {applicable_tests}")
        return PICSApplicableTestCases(test_cases=applicable_tests)

    test_collections = test_script_manager.test_collections
    enabled_pics = set([item.number for item in pics.all_enabled_items()])

    for test_collection in test_collections.values():
        for test_suite in test_collection.test_suites.values():
            for test_case in test_suite.test_cases.values():
                if len(test_case.pics) == 0:
                    # Test cases without pics required are always applicable
                    applicable_tests.add(test_case.metadata["title"])
                elif len(test_case.pics) > 0:
                    if test_case.pics.issubset(enabled_pics):
                        applicable_tests.add(test_case.metadata["title"])

    logger.debug(f"Applicable test cases: {applicable_tests}")
    return PICSApplicableTestCases(test_cases=applicable_tests)
