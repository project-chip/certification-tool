from pathlib import Path
from unittest import mock

from app.tests.yaml_tests.test_test_case import yaml_test_instance
from test_collections.yaml_tests.models.yaml_test_models import (
    YamlTestStep,
    YamlTestType,
)
from test_collections.yaml_tests.models.yaml_test_parser import (
    _test_type,
    parse_yaml_test,
)

sample_yaml_file_content = """
name: XX.YY.ZZ [TC-TEST-2.1] Simple Test

PICS:
    - ACL.S

config:
    nodeId: 0x12344321
    cluster: "Access Control"
    endpoint: 0

tests:
    - label: "Wait for the commissioned device to be retrieved"
      cluster: "DelayCommands"
      command: "WaitForCommissionee"
      arguments:
          values:
              - name: "nodeId"
                value: nodeId

"""


def test_yaml_file_parser() -> None:
    file_path = Path("/test/file.yaml")

    # We mock builtin `open` method to read sample yaml file content,
    # to avoid having to load a real file.
    with mock.patch(
        "test_collections.yaml_tests.models.yaml_test_parser.open",
        new=mock.mock_open(read_data=sample_yaml_file_content),
    ) as file_open:
        test = parse_yaml_test(file_path)

        file_open.assert_called_once_with(file_path, "r")
        assert test.path == file_path


def test_test_type_all_disabled_steps() -> None:
    disabled_step = YamlTestStep(label="Disabled Test Step", disabled=True)
    five_disabled_steps_test = yaml_test_instance(tests=[disabled_step] * 5)

    type = _test_type(five_disabled_steps_test)
    assert type == YamlTestType.MANUAL

    # simulated in path overrides test type to simulated
    five_disabled_steps_test.path = Path("TC_XX_Simulated.yaml")
    type = _test_type(five_disabled_steps_test)
    assert type == YamlTestType.SIMULATED


def test_test_type_some_disabled_steps() -> None:
    disabled_step = YamlTestStep(label="Disabled Test Step", disabled=True)
    enabled_step = YamlTestStep(label="Enabled Test Step", disabled=False)
    test = yaml_test_instance(tests=[disabled_step, enabled_step])

    type = _test_type(test)
    assert type == YamlTestType.AUTOMATED

    # simulated in path overrides test type to simulated
    test.path = Path("TC_XX_Simulated.yaml")
    type = _test_type(test)
    assert type == YamlTestType.SIMULATED


def test_test_type_all_enabled_steps_no_prompts() -> None:
    enabled_step = YamlTestStep(label="Enabled Test Step")
    five_enabled_steps_test = yaml_test_instance(tests=[enabled_step] * 5)

    type = _test_type(five_enabled_steps_test)
    assert type == YamlTestType.AUTOMATED

    # simulated in path overrides test type to simulated
    five_enabled_steps_test.path = Path("TC_XX_Simulated.yaml")
    type = _test_type(five_enabled_steps_test)
    assert type == YamlTestType.SIMULATED


def test_test_type_all_enabled_steps_some_prompts() -> None:
    enabled_step = YamlTestStep(label="Enable Test Step")
    prompt_step = YamlTestStep(label="Prompt Test Step", command="UserPrompt")
    test = yaml_test_instance(tests=[enabled_step, prompt_step])

    type = _test_type(test)
    assert type == YamlTestType.SEMI_AUTOMATED

    # simulated in path overrides test type to simulated
    test.path = Path("TC_XX_Simulated.yaml")
    type = _test_type(test)
    assert type == YamlTestType.SIMULATED
