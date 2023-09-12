from typing import Dict, List, Type

from sqlalchemy.orm import Session

from app.models import (
    TestCaseExecution,
    TestCaseMetadata,
    TestRunExecution,
    TestStepExecution,
    TestSuiteExecution,
    TestSuiteMetadata,
)
from app.schemas.test_selection import (
    TestCaseSelection,
    TestSelection,
    TestSuiteSelection,
)
from app.singleton import Singleton
from app.test_engine.models.test_run import TestRun

from .models import TestCase, TestSuite
from .models.test_declarations import (
    TestCaseDeclaration,
    TestCollectionDeclaration,
    TestSuiteDeclaration,
)
from .test_collection_discovery import discover_test_collections

# Type alias:
TestSuiteClassType = Type[TestSuite]
TestCaseClassType = Type[TestCase]


class TestNotFound(Exception):
    __test__ = False


class TestCollectionNotFound(TestNotFound):
    __test__ = False


class TestSuiteNotFound(TestNotFound):
    __test__ = False


class TestCaseNotFound(TestNotFound):
    __test__ = False


class TestScriptManager(object, metaclass=Singleton):
    __test__ = False

    test_collections: Dict[str, TestCollectionDeclaration]

    def __init__(self) -> None:
        """
        Dynamically discover test collections, ignoring internal test collections.
        """
        self.test_collections = discover_test_collections()

    def pending_test_suite_executions_for_selected_tests(
        self, selected_tests: TestSelection
    ) -> List[TestSuiteExecution]:
        """
        This will create and associate pending test suites and test cases, based on the
        selected test cases.
        """
        result = []

        # Create models within each selected Test Collection
        for test_collection_name in selected_tests.keys():
            # Lookup selected test collection:
            test_collection = self.test_collections[test_collection_name]

            test_suites = self.__pending_test_suites_for_test_collection(
                test_collection=test_collection,
                selected_test_suites=selected_tests[test_collection_name],
            )
            result.extend(test_suites)

        return result

    def __pending_test_suites_for_test_collection(
        self,
        test_collection: TestCollectionDeclaration,
        selected_test_suites: Dict[str, dict],
    ) -> List[TestSuiteExecution]:
        # Return Value
        test_suites = []

        # Unwrap the Selected Test Suites (and create models for each)
        for test_suite_id in selected_test_suites.keys():
            # Lookup selected test suite
            if test_suite_id not in test_collection.test_suites.keys():
                raise TestSuiteNotFound(f"Could not find test suite: {test_suite_id}")

            test_suite = test_collection.test_suites[test_suite_id]

            # Create pending test suite
            test_suite_execution = self.__pending_test_suite_execution(test_suite)

            # Create pending test cases
            test_cases = self.___pending_test_cases_for_test_suite(
                test_suite=test_suite,
                selected_test_cases=selected_test_suites[test_suite_id],
            )

            # Add test cases to test suite
            test_suite_execution.test_case_executions.extend(test_cases)

            test_suites.append(test_suite_execution)

        return test_suites

    def __pending_test_suite_execution(
        self,
        test_suite: TestSuiteDeclaration,
    ) -> TestSuiteExecution:
        """
        This will create a DB entry for test suite.
        """

        # Existing test suite not found creating a new one.
        metadata = self.__find_or_create_test_suite_metadata(test_suite=test_suite)

        test_suite_execution = TestSuiteExecution(
            public_id=metadata.public_id, test_suite_metadata=metadata
        )
        return test_suite_execution

    def ___pending_test_cases_for_test_suite(
        self,
        test_suite: TestSuiteDeclaration,
        selected_test_cases: Dict[str, int],
    ) -> List[TestCaseExecution]:
        # Return Value
        suite_test_cases = []

        for test_case_id, iterations in selected_test_cases.items():
            # Create pending test cases for each iteration
            test_case_declaration = self.__test_case_declaration(
                public_id=test_case_id, test_suite_declaration=test_suite
            )
            test_cases = self.__pending_test_cases_for_iterations(
                test_case=test_case_declaration, iterations=iterations
            )
            suite_test_cases.extend(test_cases)

        return suite_test_cases

    def __pending_test_cases_for_iterations(
        self, test_case: TestCaseDeclaration, iterations: int
    ) -> List[TestCaseExecution]:
        """
        This will create and associate pending test case executions, based on the number
        of iterations.
        """
        metadata = self.__find_or_create_test_case_metadata(test_case=test_case)
        test_cases = []
        for _ in range(0, iterations):
            test_case_execution = TestCaseExecution(
                public_id=metadata.public_id,
                test_case_metadata=metadata,
            )
            test_cases.append(test_case_execution)

        return test_cases

    def __find_or_create_test_suite_metadata(
        self, test_suite: TestSuiteDeclaration
    ) -> TestSuiteMetadata:
        """
        Based on test suite class reference, return a TestSuiteMetadata record.
        This will check for existing record, and validate the source hash and version.
        If no match is found, a new updated record will be created
        """

        # TODO: implement real hash check
        source_hash = "de7f3c1390cd283f91f74a334aaf0ec3"

        # TODO: check if metadata exists before creating
        return TestSuiteMetadata(**test_suite.metadata, source_hash=source_hash)

    def __find_or_create_test_case_metadata(
        self, test_case: TestCaseDeclaration
    ) -> TestCaseMetadata:
        """
        Based on test case class reference, return a TestCaseMetadata record.
        This will check for existing record, and validate the source hash and version.
        If no match is found, a new updated record will be created
        """

        # TODO: implement real hash check
        source_hash = "de7f3c1390cd283f91f74a334aaf0ec3"

        # TODO: check if metadata exists before creating
        return TestCaseMetadata(**test_case.metadata, source_hash=source_hash)

    def get_test_run(
        self,
        db: Session,
        test_run_execution: TestRunExecution,
    ) -> TestRun:
        test_run = TestRun(test_run_execution)
        self.__load_test_run_test_suites(db=db, test_run=test_run)
        return test_run

    def __load_test_run_test_suites(self, db: Session, test_run: TestRun) -> None:
        test_run.test_suites = []
        for test_suite_execution in test_run.test_run_execution.test_suite_executions:
            # TODO: error handling for TestSuite Missing
            # TODO: Security: Validate TestSuite format with regex,
            # cannot allow arbitrary strings.
            test_suite_declaration = self.__test_suite_declaration(
                test_suite_execution.public_id
            )
            TestSuiteClass = test_suite_declaration.class_ref
            test_suite = TestSuiteClass(test_suite_execution=test_suite_execution)
            self.__load_test_suite_test_cases(
                db,
                test_suite=test_suite,
                test_suite_declaration=test_suite_declaration,
                test_case_executions=test_suite_execution.test_case_executions,
            )
            test_run.test_suites.append(test_suite)

    def __test_suite_declaration(self, public_id: str) -> TestSuiteDeclaration:
        # search all collections for test suite
        for collection in self.test_collections.values():
            if public_id in collection.test_suites.keys():
                return collection.test_suites[public_id]

        raise TestSuiteNotFound(
            f"Could not find test_suite with public id: {public_id}"
        )

    def __test_case_declaration(
        self, public_id: str, test_suite_declaration: TestSuiteDeclaration
    ) -> TestCaseDeclaration:
        if public_id not in test_suite_declaration.test_cases.keys():
            raise TestCaseNotFound(
                f"Could not find test_suite with public id: {public_id}"
            )

        return test_suite_declaration.test_cases[public_id]

    def __load_test_suite_test_cases(
        self,
        db: Session,
        test_suite: TestSuite,
        test_suite_declaration: TestSuiteDeclaration,
        test_case_executions: List[TestCaseExecution],
    ) -> None:
        test_suite.test_cases = []
        for test_case_execution in test_case_executions:
            # TODO: request correct TestCase from TestScriptManager
            test_case_declaration = self.__test_case_declaration(
                test_case_execution.public_id,
                test_suite_declaration=test_suite_declaration,
            )
            TestCaseClass = test_case_declaration.class_ref
            test_case = TestCaseClass(test_case_execution=test_case_execution)
            self.create_pending_teststeps_execution(db, test_case, test_case_execution)
            test_suite.test_cases.append(test_case)

    def create_pending_teststeps_execution(
        self,
        db: Session,
        test_case: TestCase,
        test_case_execution: TestCaseExecution,
    ) -> None:
        execution_index = 0
        for test_step in test_case.test_steps:
            test_step_execution = TestStepExecution(
                title=test_step.name,
                execution_index=execution_index,
                test_case_execution_id=test_case_execution.id,
            )
            db.add(test_step_execution)
            test_step.test_step_execution = test_step_execution
            execution_index += 1
        db.commit()

    def available_test_suites(self) -> dict:
        return self.test_collections

    def validate_test_selection(self, selection: TestSelection) -> None:
        for selected_collection_name in selection.keys():
            # Check collection is in test_collections
            if selected_collection_name not in self.test_collections.keys():
                raise TestCollectionNotFound(
                    "Could not find selected test collection with name: "
                    + selected_collection_name
                )

            self.__validate_test_suite_selection_in_collection(
                selection=selection[selected_collection_name],
                collection=self.test_collections[selected_collection_name],
            )

    def __validate_test_suite_selection_in_collection(
        self,
        selection: TestSuiteSelection,
        collection: TestCollectionDeclaration,
    ) -> None:
        for selected_test_suite_id in selection.keys():
            if selected_test_suite_id not in collection.test_suites.keys():
                raise TestSuiteNotFound(
                    "Could not find selected test suite with public id: "
                    + str(selected_test_suite_id)
                )

            self.__validate_test_case_selection_in_collection(
                selection=selection[selected_test_suite_id],
                collection=collection.test_suites[selected_test_suite_id],
            )

    def __validate_test_case_selection_in_collection(
        self,
        selection: TestCaseSelection,
        collection: TestSuiteDeclaration,
    ) -> None:
        for selected_test_case_id in selection.keys():
            if selected_test_case_id not in collection.test_cases.keys():
                raise TestCaseNotFound(
                    "Could not find selected test case with public id: "
                    + str(selected_test_case_id)
                )


test_script_manager = TestScriptManager()
