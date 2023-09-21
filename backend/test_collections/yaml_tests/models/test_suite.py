from enum import Enum
from typing import Type, TypeVar

from app.chip_tool.chip_tool import ChipToolTestType
from app.chip_tool.test_suite import ChipToolSuite
from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestSuite


class YamlTestSuiteFactoryError(Exception):
    pass


class SuiteType(Enum):
    SIMULATED = 1
    AUTOMATED = 2
    MANUAL = 3


# Custom Type variable used to annotate the factory methods of classmethod.
T = TypeVar("T", bound="YamlTestSuite")


class YamlTestSuite(TestSuite):
    """Base class for all YAML based test suites.

    This class provides a class factory that will dynamically declare a new sub-class
    based on the suite-type.
    """

    yaml_version: str
    suite_name: str

    async def setup(self) -> None:
        """Override Setup to log YAML version."""
        logger.info(f"YAML Version: {self.yaml_version}")

    @classmethod
    def class_factory(
        cls, suite_type: SuiteType, name: str, yaml_version: str
    ) -> Type[T]:
        """Dynamically declares a subclass based on the type of test suite."""
        suite_class = YamlTestSuite

        if suite_type == SuiteType.MANUAL:
            suite_class = ManualYamlTestSuite
        elif suite_type == SuiteType.SIMULATED:
            suite_class = SimulatedYamlTestSuite
        elif suite_type == SuiteType.AUTOMATED:
            suite_class = ChipToolYamlTestSuite

        return suite_class.__class_factory(name=name, yaml_version=yaml_version)

    @classmethod
    def __class_factory(cls, name: str, yaml_version: str) -> Type[T]:
        """Common class factory method for all subclasses of YamlTestSuite."""

        return type(
            name,
            (cls,),
            {
                "name": name,
                "yaml_version": yaml_version,
                "metadata": {
                    "public_id": name,
                    "version": "0.0.1",
                    "title": name,
                    "description": name,
                },
            },
        )


class ManualYamlTestSuite(YamlTestSuite):
    async def setup(self) -> None:
        await super().setup()
        logger.info("This is the MANUAL test suite setup.")

    async def cleanup(self) -> None:
        logger.info("This is the MANUAL test suite cleanup.")


class ChipToolYamlTestSuite(YamlTestSuite, ChipToolSuite):
    test_type = ChipToolTestType.CHIP_TOOL

    async def setup(self) -> None:
        """Due top multi inheritance, we need to call setup on both super classes."""
        await YamlTestSuite.setup(self)
        await ChipToolSuite.setup(self)


class SimulatedYamlTestSuite(ChipToolYamlTestSuite):
    test_type = ChipToolTestType.CHIP_APP
