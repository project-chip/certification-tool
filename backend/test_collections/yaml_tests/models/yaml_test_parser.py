from pathlib import Path

from .yaml_test_models import YamlTest, YamlTestType


def _test_type(test: YamlTest) -> YamlTestType:
    """Determine the type of a test based on the parsed yaml.

    This is mainly determined by the number of disabled test steps.

    Args:
        test (YamlTest): parsed yaml model

    Returns:
        TestType:
            - Manual: All steps disabled
            - Semi-Automated: some steps are disabled
            - Automated: no disabled steps
            - Simulated: Tests where file name have "Simulated"
    """
    if test.path is not None and "Simulated" in str(test.path):
        return YamlTestType.SIMULATED

    steps = test.steps

    # If all disabled:
    if all(s.disabled is True for s in steps):
        return YamlTestType.MANUAL

    # if any step has a UserPrompt, categorize as semi-automated
    if any(s.command == "UserPrompt" for s in steps):
        return YamlTestType.SEMI_AUTOMATED

    # Otherwise Automated
    return YamlTestType.AUTOMATED


def parse_yaml_test(path: Path) -> YamlTest:
    """Parse a single YAML file into YamlTest model.

    This will also annotate parsed yaml with it's path and test type.
    """
    with open(path, "r") as file:
        yaml_str = file.read()
        test = YamlTest.parse_raw(yaml_str, proto="yaml")
        test.path = path
        test.type = _test_type(test)
        return test
