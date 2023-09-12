import importlib
import traceback
from inspect import getmembers, isclass
from os import scandir
from pathlib import Path
from pkgutil import walk_packages
from typing import Dict, List, Optional, Type, TypeVar

from loguru import logger

from app.test_engine.models import TestCase, TestSuite

from .models.test_declarations import (
    TestCaseDeclaration,
    TestCollectionDeclaration,
    TestSuiteDeclaration,
)

T = TypeVar("T")
COLLECTIONS_DIRNAME = "test_collections"
DISABLED_COLLECTIONS_FILENAME = ".disabled_test_collections"
DISABLED_TEST_CASES_FILENAME = ".disabled_test_cases"

ROOT_PATH = Path(__file__).parent.parent.parent
COLLECTIONS_PATH = ROOT_PATH / COLLECTIONS_DIRNAME
DISABLED_COLLECTIONS_FILEPATH = COLLECTIONS_PATH / DISABLED_COLLECTIONS_FILENAME
DISABLED_TEST_CASES_FILEPATH = COLLECTIONS_PATH / DISABLED_TEST_CASES_FILENAME


def disabled_test_collections() -> Optional[List[str]]:
    """Returns a list of collection names that should be disabled.

    Each line in the file at DISABLED_COLLECTIONS_FILEPATH corresponds to a
    folder/collection name to be disabled.

    File content example:
        tool_unit_tests

    Returns:
        List[str]: list of filtered folder names
    """
    return __extract_lines_from_file(DISABLED_COLLECTIONS_FILEPATH)


def disabled_test_cases() -> Optional[List[str]]:
    """Returns a list of public ids from test cases that should be disabled.

    Each line in the file at DISABLED_TEST_CASES_FILEPATH corresponds to a test case
    public id to be disabled.

    File content example:
        TC_ACL_2_1

    Returns:
        List[str]: list of filtered test case public ids
    """
    return __extract_lines_from_file(DISABLED_TEST_CASES_FILEPATH)


def __extract_lines_from_file(file_path: Path) -> Optional[List[str]]:
    """Returns a list of strings extracted from a file.

    Each line in the file corresponds to a item in the list.

    Returns:
        List[str]: list of file lines
    """
    if not file_path.exists():
        logger.warning(f"No file found at #{file_path}")
        return None

    # Load the config from file as a dictionary.
    with open(file_path) as file:
        return file.read().splitlines()


def discover_test_collections(
    disabled_collections: Optional[list[str]] = disabled_test_collections(),
    disabled_test_cases: Optional[list[str]] = disabled_test_cases(),
) -> Dict[str, TestCollectionDeclaration]:
    """Dynamically discover test_collection modules in `test_collections` folder.

    Collections will be discovered in two ways:

    - Directly declared TestCollectionDeclaration variables in the module
    initializers. Eg. `yaml_tests`

    - Dynamically generated collection based on scanning a subfolder for TestSuite and
    TestCase classes. Eg. `sample_tests`

    Note that disabled_test_cases and disabled_collections can be used to disable both
    entire collections or individual test cases.
    """
    collections: Dict[str, TestCollectionDeclaration] = {}

    names = __test_collection_folder_names()

    # Apply filter if needed
    if disabled_collections:
        names = [n for n in names if n not in disabled_collections]

    for name in names:
        # Don't add collection if it doesn't have any suites
        if found_collections := __find_test_collections(name, disabled_test_cases):
            for collection in found_collections:
                collections[collection.name] = collection

    return collections


def __find_classes_of_type(module_name: str, classtype: Type[T]) -> List[Type[T]]:
    """Dynamically find classes of specified type in the specified module.

    Limitations:
    - Finds classes by importing packages so desired classes have to be discoverable
    that way, i.e. classes are in a package and imported into the __init__.py file.
    """
    module = importlib.import_module(module_name)

    # module.__file__ is of type:
    #   - collections: '<COLLECTIONS_PATH>/<collection>/__init__.py'
    #   - test suites: '<COLLECTIONS_PATH>/<collection>/<suite>/<suite_file>.py'
    # We want to find the classes in the same level as the specified module, so we use
    # the parent as the path in walk_packages
    file_path = module.__file__

    # __file__ is optional because "It might be missing for certain types of modules,
    # such as C modules that are statically linked into the interpreter, and  the import
    # system may opt to leave it unset if it has no semantic meaning" (Python docs)
    if not file_path:
        logger.warning(f"for {module_name} __file__ was unexpectedly None.")
        return []
    package_path = Path(file_path).parent

    # Prefix to add to the module names found in walk_packages
    module_package = module.__package__
    if not module_package:
        return []
    prefix = module_package + "."

    classes = []
    for _, submodule_name, is_package in walk_packages([str(package_path)], prefix):
        if is_package:
            try:
                submodule = importlib.import_module(submodule_name)

            except Exception:
                logger.error(traceback.format_exc())

            for _, obj in getmembers(submodule):
                if isclass(obj) and issubclass(obj, classtype):
                    classes.append(obj)

    return classes


def __declared_collection_declarations(
    collection_module_name: str,
) -> list[TestCollectionDeclaration]:
    """This will check '<COLLECTIONS_PATH>/<collection>/__init__.py' for declarations of
    one or more TestCollectionDeclarations.
    """
    collections = []
    module = importlib.import_module(collection_module_name)
    for _, obj in getmembers(module):
        if isinstance(obj, TestCollectionDeclaration):
            collections.append(obj)

    return collections


def __find_test_collections(
    folder_name: str,
    disabled_test_cases: Optional[list[str]],
) -> Optional[list[TestCollectionDeclaration]]:
    """Finds test collections based on folder name.

    Either by:
    - finding pre-declared TestCollectionDeclarations declared in a module.
    - dynamically scanning the specified folder for TestSuites (based on class)
      including their TestCases.

    Limitations:
    - Finds suites / test cases by importing packages so desired classes have to be
    discoverable that way, i.e. classes are in a package.
    - TestSuites cannot be nested, i.e. one  root TestSuite for a set of test cases.
    - TestCases are nested within a TestSuite.
    """
    collection_path = f"{COLLECTIONS_PATH}/{folder_name}"
    collection_module_name = f"{COLLECTIONS_DIRNAME}.{folder_name}"

    # If Collection defines a TestCollectionDeclarations return them
    if test_collections := __declared_collection_declarations(collection_module_name):
        return test_collections

    # Return value place holder
    test_collection = TestCollectionDeclaration(path=collection_path, name=folder_name)

    test_suites: List[Type[TestSuite]] = __find_classes_of_type(
        module_name=collection_module_name, classtype=TestSuite
    )

    for suite in test_suites:
        suite_declaration = __find_test_suite(
            suite=suite,
            disabled_test_cases=disabled_test_cases,
        )

        if suite_declaration:
            test_collection.test_suites[suite.public_id()] = suite_declaration

    # Don't include empty test collections
    if not test_collection.test_suites:
        return None

    return [test_collection]


def __find_test_suite(
    suite: Type[TestSuite],
    disabled_test_cases: Optional[list[str]],
) -> Optional[TestSuiteDeclaration]:
    """Dynamically finds TestCases in the specified suite.

    Limitations:
    - Finds test cases by importing packages so desired classes have to be discoverable
    that way, i.e. classes are in a package.
    - TestCases are nested within a TestSuite.
    """
    test_cases: List[Type[TestCase]] = __find_classes_of_type(
        module_name=suite.__module__, classtype=TestCase
    )

    # Apply filter if needed
    if disabled_test_cases:
        test_cases = [x for x in test_cases if x.public_id() not in disabled_test_cases]

    # Don't include empty test suites
    if not test_cases:
        return None

    suite_declaration = TestSuiteDeclaration(suite)
    for test in test_cases:
        test_declaration = TestCaseDeclaration(test)
        suite_declaration.test_cases[test.public_id()] = test_declaration

    return suite_declaration


def __test_collection_folder_names() -> List[str]:
    """This will return all folder names for sub-folder in the test collections
    folder.

    Returns:
        List[str]: list of all folder names
    """
    return [f.name for f in scandir(COLLECTIONS_PATH) if f.is_dir()]
