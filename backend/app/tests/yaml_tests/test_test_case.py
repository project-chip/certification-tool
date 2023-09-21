from pathlib import Path
from typing import Any, Optional, Type
from unittest import mock

import pytest

from app.chip_tool.chip_tool import ChipToolTestType
from app.chip_tool.test_case import TestError
from app.models.test_case_execution import TestCaseExecution
from app.test_engine.logger import test_engine_logger
from app.test_engine.models.manual_test_case import ManualVerificationTestStep
from test_collections.yaml_tests.models import YamlTestCase
from test_collections.yaml_tests.models.test_case import (
    YamlChipToolTestCase,
    YamlManualTestCase,
    YamlSemiAutomatedChipToolTestCase,
    YamlSimulatedTestCase,
)
from test_collections.yaml_tests.models.yaml_test_models import (
    YamlTest,
    YamlTestStep,
    YamlTestType,
)


def yaml_test_instance(
    name: str = "Test Yaml",
    PICS: set[str] = {"PICS.A", "PICS.B"},
    config: dict[str, Any] = {
        "param1": "value1",
        "param2": {"type": "config_type", "defaultValue": "value2"},
    },
    tests: list[YamlTestStep] = [],
    type: YamlTestType = YamlTestType.AUTOMATED,
    path: Optional[Path] = None,
) -> YamlTest:
    return YamlTest(
        name=name,
        PICS=PICS,
        config=config,
        tests=tests,
        type=type,
        path=path,
    )


def test_yaml_test_name() -> None:
    """Test that test name is set as description in metadata."""
    name = "Another Test Name"
    test = yaml_test_instance(name=name)

    # Create a subclass of YamlTest
    case_class: Type[YamlTestCase] = YamlTestCase.class_factory(
        test=test, yaml_version="version"
    )
    assert case_class.metadata["description"] == name


def test_yaml_test_yaml_version() -> None:
    """Test that test case yaml version is set correctly in class factory."""
    test = yaml_test_instance()
    yaml_version = "best_version"
    # Create a subclass of YamlTest
    case_class: Type[YamlTestCase] = YamlTestCase.class_factory(
        test=test, yaml_version=yaml_version
    )
    assert case_class.yaml_version == yaml_version


def test_yaml_test_yaml() -> None:
    """Test that test yaml_test property is as expected in subclass of YamlTestCase."""
    test = yaml_test_instance()
    # Create a subclass of YamlTest
    case_class: Type[YamlTestCase] = YamlTestCase.class_factory(
        test=test, yaml_version="version"
    )
    assert case_class.yaml_test is test


def test_yaml_test_case_class_pics() -> None:
    """Test that the PICS of the yaml is available in the class method PICS on
    TestCase."""
    test_PICS = set(["PICS.D", "PICS.C"])
    test = yaml_test_instance(PICS=test_PICS)

    # Create a subclass of YamlTest
    case_class: Type[YamlTestCase] = YamlTestCase.class_factory(
        test=test, yaml_version="version"
    )
    assert case_class.pics() == test_PICS


def test_yaml_test_case_class_default_test_parameters() -> None:
    """Test that the default_test_parameters of the yaml is available in the class
    method default_test_parameters on TestCase.

    Also parameters with type in YAML should be flattened and type dropped."""

    test_input_config = {
        "param1": "value1",
        "param2": {"type": "config_type", "defaultValue": "value2"},
    }

    test = yaml_test_instance(config=test_input_config)
    expected_default_test_parameters = {"param1": "value1", "param2": "value2"}

    # Create a subclass of YamlTest
    case_class: Type[YamlTestCase] = YamlTestCase.class_factory(
        test=test, yaml_version="version"
    )
    assert case_class.default_test_parameters() == expected_default_test_parameters


def test_manual_test_case_class_factory_subclass_mapping() -> None:
    """Test Manual tests are created as a subclass of YamlManualTestCase."""
    test = yaml_test_instance(type=YamlTestType.MANUAL)
    case_class: Type[YamlTestCase] = YamlTestCase.class_factory(
        test=test, yaml_version="version"
    )
    assert issubclass(case_class, YamlManualTestCase)


def test_automated_test_case_class_factory_subclass_mapping() -> None:
    """Test Automated tests are created as a subclass of
    YamlChipToolTestCase."""
    test = yaml_test_instance(type=YamlTestType.AUTOMATED)
    case_class: Type[YamlTestCase] = YamlTestCase.class_factory(
        test=test, yaml_version="version"
    )
    assert issubclass(case_class, YamlChipToolTestCase)


def test_semi_automated_test_case_class_factory_subclass_mapping() -> None:
    """Test Semi-Automated tests are created as a subclass of
    YamlSemiAutomatedChipToolTestCase."""
    test = yaml_test_instance(type=YamlTestType.SEMI_AUTOMATED)
    case_class: Type[YamlTestCase] = YamlTestCase.class_factory(
        test=test, yaml_version="version"
    )
    assert issubclass(case_class, YamlSemiAutomatedChipToolTestCase)


def test_simulated_test_case_class_factory_subclass_mapping() -> None:
    """Test Simulated tests are created as a subclass of
    YamlSimulatedTestCase."""
    test = yaml_test_instance(type=YamlTestType.SIMULATED)
    case_class: Type[YamlTestCase] = YamlTestCase.class_factory(
        test=test, yaml_version="version"
    )
    assert issubclass(case_class, YamlSimulatedTestCase)


def test_incomplete_test_case_class_factory_subclass_mapping() -> None:
    """Test Semi-Automated tests are created as a subclass of
    YamlSimulatedTestCase."""
    test = yaml_test_instance(type=YamlTestType.SIMULATED)
    case_class: Type[YamlTestCase] = YamlTestCase.class_factory(
        test=test, yaml_version="version"
    )
    assert issubclass(case_class, YamlSimulatedTestCase)


def test_class_factory_test_public_id() -> None:
    """Test that class factory correctly finds identifier 'TC-XX-1.1' in yaml name.
    And set it as public_id in metadata"""
    test_data = [
        {"name": "TC-AB-1.2", "public_id": "TC-AB-1.2"},
        {"name": "[TC-CD-3.4]", "public_id": "TC-CD-3.4"},
        {"name": "Test Name before [TC-EF-5.6]", "public_id": "TC-EF-5.6"},
        {"name": "[TC-GH-7.8] Test Name after", "public_id": "TC-GH-7.8"},
        {"name": "Before and [TC-IJ-9.0] after", "public_id": "TC-IJ-9.0"},
        {"name": "Before and TC-KL-10.11 after", "public_id": "TC-KL-10.11"},
        {"name": "TC-MORE-NAME-13.110", "public_id": "TC-MORE-NAME-13.110"},
    ]
    for data in test_data:
        test = yaml_test_instance(name=data["name"])
        case_class: Type[YamlTestCase] = YamlTestCase.class_factory(
            test=test, yaml_version="version"
        )
        assert case_class.metadata["public_id"] == data["public_id"]


def test_class_factory_test_class_name() -> None:
    """Test that class factory correctly finds identifier 'TC-XX-1.1', convert it to
    a safe class name, eg TC_XX_1_1"""
    test_data = [
        {"name": "TC-AB-1.2", "class_name": "TC_AB_1_2"},
        {"name": "[TC-CD-3.4]", "class_name": "TC_CD_3_4"},
        {"name": "Test Name before [TC-EF-5.6]", "class_name": "TC_EF_5_6"},
        {"name": "[TC-GH-7.8] Test Name after", "class_name": "TC_GH_7_8"},
        {"name": "Before and [TC-IJ-9.0] after", "class_name": "TC_IJ_9_0"},
        {"name": "Before and TC-KL-10.11 after", "class_name": "TC_KL_10_11"},
        {"name": "TC-MORE-NAME-13.110", "class_name": "TC_MORE_NAME_13_110"},
    ]
    for data in test_data:
        test = yaml_test_instance(name=data["name"])
        case_class: Type[YamlTestCase] = YamlTestCase.class_factory(
            test=test, yaml_version="version"
        )
        assert case_class.__name__ == data["class_name"]


def test_class_factory_test_title_semi_automated() -> None:
    """Test that class factory correctly finds identifier 'TC-XX-1.1', use it as
    metadata title, and append (Semi-automated) when appropriate."""

    for type in list(YamlTestType):
        test = yaml_test_instance(type=type, name="TC-AB-1.2")
        case_class: Type[YamlTestCase] = YamlTestCase.class_factory(
            test=test, yaml_version="version"
        )

        if type == YamlTestType.SEMI_AUTOMATED:
            assert test.name in case_class.metadata["title"]
            assert "(Semi-automated)" in case_class.metadata["title"]
        else:
            assert case_class.metadata["title"] == test.name


def test_class_factory_test_title_steps_disabled() -> None:
    """Test that class factory correctly finds identifier 'TC-XX-1.1', use it as
    metadata title, and (Steps Disabled) when some but not all steps are disabled."""
    disabled_step = YamlTestStep(label="Step1", disabled=True)
    enabled_step = YamlTestStep(label="Step2", disabled=False)
    for type in [
        YamlTestType.AUTOMATED,
        YamlTestType.SEMI_AUTOMATED,
        YamlTestType.SIMULATED,
    ]:
        test = yaml_test_instance(
            type=type, name="TC-AB-1.2", tests=[disabled_step, enabled_step]
        )
        case_class: Type[YamlTestCase] = YamlTestCase.class_factory(
            test=test, yaml_version="version"
        )
        assert test.name in case_class.metadata["title"]
        assert "(Steps Disabled)" in case_class.metadata["title"]


def test_steps_in_manual_yaml_test_case() -> None:
    """
    This will test that manual test steps are created correctly in YamlTestCase
    subclass.
    - All steps are ManualVerificationTestStep
    - name is mapped to yaml step label
    - verification details are optional but passed when present in yaml
    """
    steps = [
        YamlTestStep(label="Step1"),
        YamlTestStep(label="Step2Verification", verification="Verification String"),
    ]
    test = yaml_test_instance(type=YamlTestType.MANUAL, tests=steps)
    case_class: Type[YamlTestCase] = YamlTestCase.class_factory(
        test=test, yaml_version="version"
    )

    test_instance = case_class(TestCaseExecution())
    # Note that a LogUpload step is added from the superclass
    assert len(steps) == len(test_instance.test_steps) - 1
    for index, step in enumerate(steps):
        step_instance = test_instance.test_steps[index]
        assert isinstance(step_instance, ManualVerificationTestStep)
        assert step_instance.name == step.label
        assert step_instance.verification == step.verification


def test_test_type_for_automated_tests() -> None:
    """Test that automated tests are set to use chip-tool"""
    test = yaml_test_instance(type=YamlTestType.AUTOMATED)
    case_class: Type[YamlTestCase] = YamlTestCase.class_factory(
        test=test, yaml_version="version"
    )
    assert issubclass(case_class, YamlChipToolTestCase)
    instance = case_class(TestCaseExecution())
    assert instance.test_type == ChipToolTestType.CHIP_TOOL


def test_test_type_for_simulated_tests() -> None:
    """Test that simulated tests are set to use chip-app"""
    test = yaml_test_instance(type=YamlTestType.SIMULATED)
    case_class: Type[YamlTestCase] = YamlTestCase.class_factory(
        test=test, yaml_version="version"
    )
    assert issubclass(case_class, YamlSimulatedTestCase)
    instance = case_class(TestCaseExecution())
    assert instance.test_type == ChipToolTestType.CHIP_APP


@pytest.mark.asyncio
async def test_yaml_version_logging() -> None:
    """Test that all YAML tests will log YAML version to test_engine_logger.

    Note that since `chip-tool` is not setup, we except the TestError raised.
    """
    for type in list(YamlTestType):
        test = yaml_test_instance(type=type)
        test_yaml_version = "YamlVersionTest"
        case_class: Type[YamlTestCase] = YamlTestCase.class_factory(
            test=test, yaml_version=test_yaml_version
        )
        instance = case_class(TestCaseExecution())

        with mock.patch.object(
            target=test_engine_logger, attribute="info"
        ) as logger_info:
            try:
                await instance.setup()
            except TestError:
                pass
            logger_info.assert_called()
            logger_info.assert_any_call(f"YAML Version: {test_yaml_version}")


def test_default_first_steps_for_yaml_chip_tool_test_case() -> None:
    test = yaml_test_instance(type=YamlTestType.AUTOMATED, tests=[])
    case_class: Type[YamlTestCase] = YamlTestCase.class_factory(
        test=test, yaml_version="version"
    )
    instance = case_class(TestCaseExecution())
    assert len(instance.test_steps) == 1
    assert instance.test_steps[0].name == "Start chip-tool test"


def test_no_default_first_steps_for_yaml_simulated_test_case() -> None:
    test = yaml_test_instance(type=YamlTestType.SIMULATED, tests=[])
    case_class: Type[YamlTestCase] = YamlTestCase.class_factory(
        test=test, yaml_version="version"
    )
    instance = case_class(TestCaseExecution())
    assert len(instance.test_steps) == 1
    assert instance.test_steps[0].name == "Start chip-app test"


def test_disabled_steps_for_non_manual_test() -> None:
    """Test that non-manual tests skip disabled steps."""
    for type in list(YamlTestType):
        if type == YamlTestType.MANUAL:
            continue
        test_step = YamlTestStep(label="Disabled Step", disabled=True)
        test = yaml_test_instance(type=type, tests=[test_step])
        case_class: Type[YamlTestCase] = YamlTestCase.class_factory(
            test=test, yaml_version="version"
        )
        instance = case_class(TestCaseExecution())
        for step in instance.test_steps:
            assert step.name != test_step.label


def test_normal_steps_for_non_manual_tests() -> None:
    """Test that non-manual tests include enabled steps."""
    for type in list(YamlTestType):
        if type == YamlTestType.MANUAL:
            continue
        test_step = YamlTestStep(label="Step1")
        test = yaml_test_instance(type=type, tests=[test_step])
        case_class: Type[YamlTestCase] = YamlTestCase.class_factory(
            test=test, yaml_version="version"
        )
        instance = case_class(TestCaseExecution())
        # Assert normal step is present
        assert len(instance.test_steps) >= 1
        assert any(s.name == test_step.label for s in instance.test_steps)


def test_multiple_steps_for_non_manual() -> None:
    """Test that non-manual tests multiple enabled steps are all included."""
    for type in list(YamlTestType):
        if type == YamlTestType.MANUAL:
            continue
        test_step = YamlTestStep(label="StepN")
        no_steps = 5
        test = yaml_test_instance(type=type, tests=([test_step] * no_steps))
        case_class: Type[YamlTestCase] = YamlTestCase.class_factory(
            test=test, yaml_version="version"
        )
        instance = case_class(TestCaseExecution())

        # Assert all steps from yaml test are added
        assert len(instance.test_steps) >= no_steps
        steps_from_yaml = [s for s in instance.test_steps if s.name == test_step.label]
        assert len(steps_from_yaml) == no_steps


def test_prompt_steps_for_yaml_chip_tool_test_case() -> None:
    test_step = YamlTestStep(
        label="Step1",
        command="UserPrompt",
        verification="Verify that This happened",
    )

    test = yaml_test_instance(type=YamlTestType.AUTOMATED, tests=[test_step])
    case_class: Type[YamlTestCase] = YamlTestCase.class_factory(
        test=test, yaml_version="version"
    )
    instance = case_class(TestCaseExecution())
    assert len(instance.test_steps) == 2
    last_step = instance.test_steps[1]
    assert isinstance(last_step, ManualVerificationTestStep)
    assert last_step.name == test_step.label
    assert last_step.verification == test_step.verification


@pytest.mark.asyncio
async def test_setup_super_error_handling() -> None:
    # ignore requirement to create_tests on init
    with mock.patch("app.test_engine.models.test_case.TestCase.create_test_steps") as _:
        test = YamlTestCase(TestCaseExecution())
        test.yaml_version = "some version"
        # Assert this doesn't raise an exception
        await test.setup()
