import os
from pathlib import Path
from uuid import uuid1

from app.test_engine.test_collection_discovery import (
    __extract_lines_from_file,
    discover_test_collections,
)


def test_extract_lines_from_file_with_existing_file_returns_lines() -> None:
    directory_path = Path(__file__).parent
    new_file_path = directory_path / f"tempFile_{uuid1()}"
    file_lines = ["str1", "str2", "str3", "str4"]

    with open(new_file_path, "x") as new_file:
        new_file.write("\n".join(file_lines))

    result = __extract_lines_from_file(new_file_path)

    os.remove(new_file_path)

    assert result == file_lines


def test_extract_lines_from_file_with_nonexisting_file_returns_none() -> None:
    directory_path = Path(__file__).parent
    new_file_path = directory_path / f"tempFile_{uuid1()}"

    result = __extract_lines_from_file(new_file_path)

    assert result is None


def test_discover_test_collections_disable_one_test_case() -> None:
    disabled_test_cases = ["TC_Blocklist_2_1"]

    collections = discover_test_collections(
        disabled_collections=None, disabled_test_cases=disabled_test_cases
    )

    test_collection_names = []
    test_suite_ids = []
    test_case_ids = []
    for collection in collections.values():
        test_collection_names.append(collection.name)
        for suite in collection.test_suites.values():
            test_suite_ids.append(suite.metadata["public_id"])
            for test_case in suite.test_cases.values():
                test_case_ids.append(test_case.metadata["public_id"])

    assert "tool_blocklist_unit_tests" in test_collection_names
    assert "TestSuiteBlocklist1" in test_suite_ids
    assert "TC_Blocklist_1_1" in test_case_ids
    assert "TestSuiteBlocklist2" in test_suite_ids
    assert "TC_Blocklist_2_1" not in test_case_ids
    assert "TC_Blocklist_2_2" in test_case_ids


def test_discover_test_collections_disable_all_test_cases_in_suite() -> None:
    disabled_test_cases = ["TC_Blocklist_2_1", "TC_Blocklist_2_2"]

    collections = discover_test_collections(
        disabled_collections=None, disabled_test_cases=disabled_test_cases
    )

    test_collection_names = []
    test_suite_ids = []
    test_case_ids = []
    for collection in collections.values():
        test_collection_names.append(collection.name)
        for suite in collection.test_suites.values():
            test_suite_ids.append(suite.metadata["public_id"])
            for test_case in suite.test_cases.values():
                test_case_ids.append(test_case.metadata["public_id"])

    assert "tool_blocklist_unit_tests" in test_collection_names
    assert "TestSuiteBlocklist1" in test_suite_ids
    assert "TC_Blocklist_1_1" in test_case_ids
    assert "TestSuiteBlocklist2" not in test_suite_ids
    assert "TC_Blocklist_2_1" not in test_case_ids
    assert "TC_Blocklist_2_2" not in test_case_ids


def test_discover_test_collections_disable_all_test_cases_in_collection() -> None:
    disabled_test_cases = ["TC_Blocklist_1_1", "TC_Blocklist_2_1", "TC_Blocklist_2_2"]

    collections = discover_test_collections(
        disabled_collections=None, disabled_test_cases=disabled_test_cases
    )

    test_collection_names = []
    test_suite_ids = []
    test_case_ids = []
    for collection in collections.values():
        test_collection_names.append(collection.name)
        for suite in collection.test_suites.values():
            test_suite_ids.append(suite.metadata["public_id"])
            for test_case in suite.test_cases.values():
                test_case_ids.append(test_case.metadata["public_id"])

    assert "tool_blocklist_unit_tests" not in test_collection_names
    assert "TestSuiteBlocklist1" not in test_suite_ids
    assert "TC_Blocklist_1_1" not in test_case_ids
    assert "TestSuiteBlocklist2" not in test_suite_ids
    assert "TC_Blocklist_2_1" not in test_case_ids
    assert "TC_Blocklist_2_2" not in test_case_ids


def test_discover_test_collections_disables_blocklist_test_cases_by_default() -> None:
    # By default discover_test_collections does not discover unit test
    # collection/suites/cases
    collections = discover_test_collections(disabled_test_cases=[])

    test_collection_names = []
    test_suite_ids = []
    test_case_ids = []
    for collection in collections.values():
        test_collection_names.append(collection.name)
        for suite in collection.test_suites.values():
            test_suite_ids.append(suite.metadata["public_id"])
            for test_case in suite.test_cases.values():
                test_case_ids.append(test_case.metadata["public_id"])

    assert "tool_blocklist_unit_tests" not in test_collection_names
    assert "TestSuiteBlocklist1" not in test_suite_ids
    assert "TC_Blocklist_1_1" not in test_case_ids
    assert "TestSuiteBlocklist2" not in test_suite_ids
    assert "TC_Blocklist_2_1" not in test_case_ids
    assert "TC_Blocklist_2_2" not in test_case_ids
