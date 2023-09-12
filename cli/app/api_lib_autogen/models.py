from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union  # noqa

from pydantic import BaseModel, Field


class BodyCreateTestRunExecutionApiV1TestRunExecutionsPost(BaseModel):
    test_run_execution_in: "TestRunExecutionCreate" = Field(..., alias="test_run_execution_in")
    selected_tests: "Optional[Dict[str, Dict[str, Dict[str, int]]]]" = Field(None, alias="selected_tests")


# class BodyUploadFileApiV1TestRunExecutionsFileUploadPost(BaseModel):
# file: "IO[Any]" = Field(..., alias="file")


class DutConfig(BaseModel):
    discriminator: "str" = Field(..., alias="discriminator")
    setup_code: "str" = Field(..., alias="setup_code")
    pairing_mode: "DutPairingModeEnum" = Field(..., alias="pairing_mode")
    ip_address: "Optional[str]" = Field(None, alias="ip_address")
    port: "Optional[str]" = Field(None, alias="port")


class DutPairingModeEnum(str, Enum):
    ETHERNET = "ethernet"
    ONNETWORK = "onnetwork"
    BLE_WIFI = "ble-wifi"
    BLE_THREAD = "ble-thread"


class HTTPValidationError(BaseModel):
    detail: "Optional[List[ValidationError]]" = Field(None, alias="detail")


class Msg(BaseModel):
    msg: "str" = Field(..., alias="msg")


class NetworkConfig(BaseModel):
    wifi: "WiFiConfig" = Field(..., alias="wifi")
    thread: "Union[ThreadAutoConfig,ThreadExternalConfig]" = Field(..., alias="thread")


class Operator(BaseModel):
    name: "str" = Field(..., alias="name")
    id: "int" = Field(..., alias="id")


class OperatorCreate(BaseModel):
    name: "str" = Field(..., alias="name")


class OperatorUpdate(BaseModel):
    name: "Optional[str]" = Field(None, alias="name")


class Project(BaseModel):
    name: "str" = Field(..., alias="name")
    config: "Optional[TestEnvironmentConfig]" = Field(None, alias="config")
    id: "int" = Field(..., alias="id")
    created_at: "datetime" = Field(..., alias="created_at")
    updated_at: "datetime" = Field(..., alias="updated_at")
    archived_at: "Optional[datetime]" = Field(None, alias="archived_at")


class ProjectCreate(BaseModel):
    name: "str" = Field(..., alias="name")
    config: "Optional[TestEnvironmentConfig]" = Field(None, alias="config")


class ProjectUpdate(BaseModel):
    name: "str" = Field(..., alias="name")
    config: "TestEnvironmentConfig" = Field(..., alias="config")


class TestCase(BaseModel):
    metadata: "TestMetadata" = Field(..., alias="metadata")


class TestCaseExecution(BaseModel):
    state: "TestStateEnum" = Field(..., alias="state")
    public_id: "str" = Field(..., alias="public_id")
    test_suite_execution_id: "int" = Field(..., alias="test_suite_execution_id")
    test_case_metadata_id: "int" = Field(..., alias="test_case_metadata_id")
    id: "int" = Field(..., alias="id")
    started_at: "Optional[datetime]" = Field(None, alias="started_at")
    completed_at: "Optional[datetime]" = Field(None, alias="completed_at")
    errors: "Optional[List[str]]" = Field(None, alias="errors")
    test_case_metadata: "TestCaseMetadata" = Field(..., alias="test_case_metadata")
    test_step_executions: "List[TestStepExecution]" = Field(..., alias="test_step_executions")


class TestCaseMetadata(BaseModel):
    public_id: "str" = Field(..., alias="public_id")
    title: "str" = Field(..., alias="title")
    description: "str" = Field(..., alias="description")
    version: "str" = Field(..., alias="version")
    source_hash: "str" = Field(..., alias="source_hash")
    id: "int" = Field(..., alias="id")


class TestCollection(BaseModel):
    name: "str" = Field(..., alias="name")
    path: "str" = Field(..., alias="path")
    test_suites: "Dict[str, TestSuite]" = Field(..., alias="test_suites")


class TestCollections(BaseModel):
    test_collections: "Dict[str, TestCollection]" = Field(..., alias="test_collections")


class TestEnvironmentConfig(BaseModel):
    network: "NetworkConfig" = Field(..., alias="network")
    dut_config: "DutConfig" = Field(..., alias="dut_config")


class TestMetadata(BaseModel):
    public_id: "str" = Field(..., alias="public_id")
    version: "str" = Field(..., alias="version")
    title: "str" = Field(..., alias="title")
    description: "str" = Field(..., alias="description")


class TestRunConfig(BaseModel):
    name: "str" = Field(..., alias="name")
    dut_name: "str" = Field(..., alias="dut_name")
    selected_tests: "Optional[Dict[str, Dict[str, Dict[str, int]]]]" = Field(None, alias="selected_tests")
    id: "int" = Field(..., alias="id")


class TestRunConfigCreate(BaseModel):
    name: "str" = Field(..., alias="name")
    dut_name: "str" = Field(..., alias="dut_name")
    selected_tests: "Optional[Dict[str, Dict[str, Dict[str, int]]]]" = Field(None, alias="selected_tests")


class TestRunConfigUpdate(BaseModel):
    name: "str" = Field(..., alias="name")


class TestRunExecution(BaseModel):
    title: "str" = Field(..., alias="title")
    test_run_config_id: "Optional[int]" = Field(None, alias="test_run_config_id")
    project_id: "Optional[int]" = Field(None, alias="project_id")
    description: "Optional[str]" = Field(None, alias="description")
    id: "int" = Field(..., alias="id")
    state: "TestStateEnum" = Field(..., alias="state")
    started_at: "Optional[datetime]" = Field(None, alias="started_at")
    completed_at: "Optional[datetime]" = Field(None, alias="completed_at")
    archived_at: "Optional[datetime]" = Field(None, alias="archived_at")
    operator: "Optional[Operator]" = Field(None, alias="operator")


class TestRunExecutionCreate(BaseModel):
    title: "str" = Field(..., alias="title")
    test_run_config_id: "Optional[int]" = Field(None, alias="test_run_config_id")
    project_id: "Optional[int]" = Field(None, alias="project_id")
    description: "Optional[str]" = Field(None, alias="description")
    operator_id: "Optional[int]" = Field(None, alias="operator_id")


class TestRunExecutionInDBBase(BaseModel):
    title: "str" = Field(..., alias="title")
    test_run_config_id: "Optional[int]" = Field(None, alias="test_run_config_id")
    project_id: "Optional[int]" = Field(None, alias="project_id")
    description: "Optional[str]" = Field(None, alias="description")
    id: "int" = Field(..., alias="id")
    state: "TestStateEnum" = Field(..., alias="state")
    started_at: "Optional[datetime]" = Field(None, alias="started_at")
    completed_at: "Optional[datetime]" = Field(None, alias="completed_at")
    archived_at: "Optional[datetime]" = Field(None, alias="archived_at")


class TestRunExecutionStats(BaseModel):
    test_case_count: "Optional[int]" = Field(None, alias="test_case_count")
    states: "Optional[Dict[str, int]]" = Field(None, alias="states")


class TestRunExecutionWithChildren(BaseModel):
    title: "str" = Field(..., alias="title")
    test_run_config_id: "Optional[int]" = Field(None, alias="test_run_config_id")
    project_id: "Optional[int]" = Field(None, alias="project_id")
    description: "Optional[str]" = Field(None, alias="description")
    id: "int" = Field(..., alias="id")
    state: "TestStateEnum" = Field(..., alias="state")
    started_at: "Optional[datetime]" = Field(None, alias="started_at")
    completed_at: "Optional[datetime]" = Field(None, alias="completed_at")
    archived_at: "Optional[datetime]" = Field(None, alias="archived_at")
    operator: "Optional[Operator]" = Field(None, alias="operator")
    test_suite_executions: "Optional[List[TestSuiteExecution]]" = Field(None, alias="test_suite_executions")


class TestRunExecutionWithStats(BaseModel):
    title: "str" = Field(..., alias="title")
    test_run_config_id: "Optional[int]" = Field(None, alias="test_run_config_id")
    project_id: "Optional[int]" = Field(None, alias="project_id")
    description: "Optional[str]" = Field(None, alias="description")
    id: "int" = Field(..., alias="id")
    state: "TestStateEnum" = Field(..., alias="state")
    started_at: "Optional[datetime]" = Field(None, alias="started_at")
    completed_at: "Optional[datetime]" = Field(None, alias="completed_at")
    archived_at: "Optional[datetime]" = Field(None, alias="archived_at")
    operator: "Optional[Operator]" = Field(None, alias="operator")
    test_case_stats: "TestRunExecutionStats" = Field(..., alias="test_case_stats")


class TestRunnerState(str, Enum):
    IDLE = "idle"
    LOADING = "loading"
    READY = "ready"
    RUNNING = "running"


class TestRunnerStatus(BaseModel):
    state: "TestRunnerState" = Field(..., alias="state")
    test_run_execution_id: "Optional[int]" = Field(None, alias="test_run_execution_id")


class TestStateEnum(str, Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    PENDING_ACTUATION = "pending_actuation"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    NOT_APPLICABLE = "not_applicable"
    CANCELLED = "cancelled"


class TestStepExecution(BaseModel):
    state: "TestStateEnum" = Field(..., alias="state")
    title: "str" = Field(..., alias="title")
    test_case_execution_id: "int" = Field(..., alias="test_case_execution_id")
    id: "int" = Field(..., alias="id")
    started_at: "Optional[datetime]" = Field(None, alias="started_at")
    completed_at: "Optional[datetime]" = Field(None, alias="completed_at")
    errors: "Optional[List[str]]" = Field(None, alias="errors")
    failures: "Optional[List[str]]" = Field(None, alias="failures")


class TestSuite(BaseModel):
    metadata: "TestMetadata" = Field(..., alias="metadata")
    test_cases: "Dict[str, TestCase]" = Field(..., alias="test_cases")


class TestSuiteExecution(BaseModel):
    state: "TestStateEnum" = Field(..., alias="state")
    public_id: "str" = Field(..., alias="public_id")
    test_run_execution_id: "int" = Field(..., alias="test_run_execution_id")
    test_suite_metadata_id: "int" = Field(..., alias="test_suite_metadata_id")
    id: "int" = Field(..., alias="id")
    started_at: "Optional[datetime]" = Field(None, alias="started_at")
    completed_at: "Optional[datetime]" = Field(None, alias="completed_at")
    errors: "Optional[List[str]]" = Field(None, alias="errors")
    test_case_executions: "List[TestCaseExecution]" = Field(..., alias="test_case_executions")
    test_suite_metadata: "TestSuiteMetadata" = Field(..., alias="test_suite_metadata")


class TestSuiteMetadata(BaseModel):
    public_id: "str" = Field(..., alias="public_id")
    title: "str" = Field(..., alias="title")
    description: "str" = Field(..., alias="description")
    version: "str" = Field(..., alias="version")
    source_hash: "str" = Field(..., alias="source_hash")
    id: "int" = Field(..., alias="id")


class ThreadAutoConfig(BaseModel):
    rcp_serial_path: "str" = Field(..., alias="rcp_serial_path")
    rcp_baudrate: "int" = Field(..., alias="rcp_baudrate")
    on_mesh_prefix: "str" = Field(..., alias="on_mesh_prefix")
    network_interface: "str" = Field(..., alias="network_interface")
    dataset: "ThreadDataset" = Field(..., alias="dataset")
    otbr_docker_image: "Optional[str]" = Field(None, alias="otbr_docker_image")


class ThreadDataset(BaseModel):
    channel: "str" = Field(..., alias="channel")
    panid: "str" = Field(..., alias="panid")
    extpanid: "str" = Field(..., alias="extpanid")
    networkkey: "str" = Field(..., alias="networkkey")
    networkname: "str" = Field(..., alias="networkname")


class ThreadExternalConfig(BaseModel):
    operational_dataset_hex: "str" = Field(..., alias="operational_dataset_hex")


class ValidationError(BaseModel):
    loc: "List[str]" = Field(..., alias="loc")
    msg: "str" = Field(..., alias="msg")
    type: "str" = Field(..., alias="type")


class WiFiConfig(BaseModel):
    ssid: "str" = Field(..., alias="ssid")
    password: "str" = Field(..., alias="password")
