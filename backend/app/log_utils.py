from datetime import datetime
from functools import reduce
from io import BytesIO
from operator import add
from typing import Generator, List, Optional
from zipfile import ZipFile

from app import models, schemas

LOG_SECTION_TEMPLATE = "--------------------- {} ---------------------\n"


def log_generator(
    log_entries: List[schemas.TestRunLogEntry], json_entries: bool
) -> Generator:
    for log_line in log_entries:
        if json_entries:
            yield log_line.json()
            yield "\n"
        else:
            timestamp = datetime.fromtimestamp(log_line.timestamp).strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            )
            yield f"{log_line.level:10} | {timestamp} | {log_line.message}\n"


def group_test_run_execution_logs(
    test_run_execution: models.TestRunExecution,
) -> schemas.GroupedTestRunExecutionLogs:
    grouped_logs = schemas.GroupedTestRunExecutionLogs()

    # Log entries have indexes for test suite, test case and test step executions. E.g.:
    #   test_suite_execution_index: 0,
    #   test_case_execution_index: 1,
    #   test_step_execution_index: 4,
    # - For general TH logs, all 3 indexes are None;
    # - For test suite specific logs (not related to any test case), the indexes for
    # test case and test step are None and the test_suite_execution_index is not None;
    # - For test case logs, the indexes for test suite and test case are not None.
    for entry in test_run_execution.log:
        if test_case := __test_case_execution_for_log_entry(
            test_run_execution=test_run_execution, log_entry=entry
        ):
            if grouped_logs.cases.get(test_case.state) is None:
                grouped_logs.cases[test_case.state] = {}

            if grouped_logs.cases[test_case.state].get(test_case.public_id) is None:
                grouped_logs.cases[test_case.state][test_case.public_id] = []

            grouped_logs.cases[test_case.state][test_case.public_id].append(entry)
        elif test_suite := __test_suite_execution_for_log_entry(
            test_run_execution=test_run_execution, log_entry=entry
        ):
            if grouped_logs.suites.get(test_suite.public_id) is None:
                grouped_logs.suites[test_suite.public_id] = []

            grouped_logs.suites[test_suite.public_id].append(entry)
        else:
            grouped_logs.general.append(entry)

    return grouped_logs


def create_grouped_log_zip_file(
    grouped_logs: schemas.GroupedTestRunExecutionLogs,
) -> BytesIO:
    file = BytesIO()

    with ZipFile(file=file, mode="w") as zip_file:
        __create_summary_file(grouped_logs=grouped_logs, zip_file=zip_file)
        __create_suites_file(grouped_logs=grouped_logs, zip_file=zip_file)

        for state in grouped_logs.cases.keys():
            __create_cases_file(
                grouped_logs=grouped_logs, state=state, zip_file=zip_file
            )

    file.seek(0)

    return file


def __test_suite_execution_for_log_entry(
    test_run_execution: models.TestRunExecution, log_entry: schemas.TestRunLogEntry
) -> Optional[models.TestSuiteExecution]:
    if (test_suite_index := log_entry.test_suite_execution_index) is None:
        return None

    return test_run_execution.test_suite_executions[test_suite_index]


def __test_case_execution_for_log_entry(
    test_run_execution: models.TestRunExecution, log_entry: schemas.TestRunLogEntry
) -> Optional[models.TestCaseExecution]:
    if (test_suite_index := log_entry.test_suite_execution_index) is None or (
        test_case_index := log_entry.test_case_execution_index
    ) is None:
        return None

    return test_run_execution.test_suite_executions[
        test_suite_index
    ].test_case_executions[test_case_index]


def __create_summary_file(
    grouped_logs: schemas.GroupedTestRunExecutionLogs, zip_file: ZipFile
) -> None:
    content: List[str] = []

    test_case_count = reduce(add, map(len, grouped_logs.cases.values()), 0)

    if test_case_count == 0:
        content.append("No test case has been executed")
    else:
        for state, test_cases in grouped_logs.cases.items():
            content.append(
                LOG_SECTION_TEMPLATE.format(
                    f'"{state}" test cases ({len(test_cases)}/{test_case_count})'
                )
            )
            for test_case_id in test_cases.keys():
                content.append(f"{test_case_id}\n")

    zip_file.writestr(zinfo_or_arcname="summary.txt", data="".join(content))


def __create_suites_file(
    grouped_logs: schemas.GroupedTestRunExecutionLogs, zip_file: ZipFile
) -> None:
    content = [LOG_SECTION_TEMPLATE.format("Test run general logs")]
    content.extend(log_generator(log_entries=grouped_logs.general, json_entries=False))

    for test_suite, test_suite_logs in grouped_logs.suites.items():
        content.append(LOG_SECTION_TEMPLATE.format(f"{test_suite} logs"))
        content.extend(log_generator(log_entries=test_suite_logs, json_entries=False))

    zip_file.writestr(
        zinfo_or_arcname="test_suites_setup_and_cleanup.log", data="".join(content)
    )


def __create_cases_file(
    grouped_logs: schemas.GroupedTestRunExecutionLogs,
    state: models.TestStateEnum,
    zip_file: ZipFile,
) -> None:
    content = [LOG_SECTION_TEMPLATE.format("Test run general logs")]
    content.extend(log_generator(log_entries=grouped_logs.general, json_entries=False))

    for test_case, test_case_logs in grouped_logs.cases[state].items():
        content.append(LOG_SECTION_TEMPLATE.format(f"{test_case} logs"))
        content.extend(log_generator(log_entries=test_case_logs, json_entries=False))

    zip_file.writestr(zinfo_or_arcname=f"{state}_test_cases.log", data="".join(content))
