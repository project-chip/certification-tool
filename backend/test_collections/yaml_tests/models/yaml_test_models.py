from enum import Enum
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field
from pydantic_yaml import YamlModelMixin

###
# This file declares YAML models that are used to parse the YAML Test Cases.
###


class YamlTestType(Enum):
    AUTOMATED = 0
    SEMI_AUTOMATED = 1
    MANUAL = 2
    SIMULATED = 3


class YamlTestStep(YamlModelMixin, BaseModel):
    label: str
    PICS: Optional[str] = None
    verification: Optional[str] = None
    command: Optional[str]
    disabled: bool = False
    arguments: Optional[dict[str, Any]]


class YamlTest(YamlModelMixin, BaseModel):
    name: str
    PICS: set[str] = set()
    config: dict[str, Any]
    steps: list[YamlTestStep] = Field(alias="tests")
    type: YamlTestType = YamlTestType.MANUAL
    path: Optional[Path]
