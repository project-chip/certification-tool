# flake8: noqa E501
from asyncio import get_event_loop
from typing import IO, TYPE_CHECKING, Any, Awaitable, Dict, List, Optional

from api_lib_autogen import models as m
from fastapi.encoders import jsonable_encoder

if TYPE_CHECKING:
    from api_lib_autogen.api_client import ApiClient


class _TestRunExecutionsApi:
    def __init__(self, api_client: "ApiClient"):
        self.api_client = api_client

    def _build_for_abort_testing_api_v1_test_run_executions_abort_testing_post(
        self,
    ) -> Awaitable[Dict[str, str]]:
        """
        Cancel the current testing
        """
        return self.api_client.request(
            type_=Dict[str, str],
            method="POST",
            url="/api/v1/test_run_executions/abort-testing",
        )

    def _build_for_archive_api_v1_test_run_executions_id_archive_post(self, id: int) -> Awaitable[m.TestRunExecution]:
        """
        Archive test run execution by id.  Args:     id (int): test run execution id  Raises:     HTTPException: if no test run execution exists for provided id  Returns:     TestRunExecution: test run execution record that was archived
        """
        path_params = {"id": str(id)}

        return self.api_client.request(
            type_=m.TestRunExecution,
            method="POST",
            url="/api/v1/test_run_executions/{id}/archive",
            path_params=path_params,
        )

    def _build_for_create_test_run_execution_api_v1_test_run_executions_post(
        self,
        body_create_test_run_execution_api_v1_test_run_executions_post: m.BodyCreateTestRunExecutionApiV1TestRunExecutionsPost,
    ) -> Awaitable[m.TestRunExecutionWithChildren]:
        """
        Create new test run execution.
        """
        body = jsonable_encoder(body_create_test_run_execution_api_v1_test_run_executions_post)

        return self.api_client.request(
            type_=m.TestRunExecutionWithChildren, method="POST", url="/api/v1/test_run_executions/", json=body
        )

    def _build_for_download_log_api_v1_test_run_executions_id_log_get(
        self, id: int, json_entries: Optional[bool] = None, download: Optional[bool] = None
    ) -> Awaitable[None]:
        """
        Download the logs from a test run.   Args:     id (int): Id of the TestRunExectution the log is requested for     json_entries (bool, optional): When set, return each log line as a json object     download (bool, optional): When set, return as attachment
        """
        path_params = {"id": str(id)}

        query_params = {}
        if json_entries is not None:
            query_params["json_entries"] = str(json_entries)
        if download is not None:
            query_params["download"] = str(download)

        return self.api_client.request(
            type_=None,
            method="GET",
            url="/api/v1/test_run_executions/{id}/log",
            path_params=path_params,
            params=query_params,
        )

    def _build_for_get_test_runner_status_api_v1_test_run_executions_status_get(
        self,
    ) -> Awaitable[m.TestRunnerStatus]:
        """
        Retrieve status of the Test Engine.  When the Test Engine is actively running the status will include the current test_run and the details of the states.
        """
        return self.api_client.request(
            type_=m.TestRunnerStatus,
            method="GET",
            url="/api/v1/test_run_executions/status",
        )

    def _build_for_read_test_run_execution_api_v1_test_run_executions_id_get(
        self, id: int
    ) -> Awaitable[m.TestRunExecutionWithChildren]:
        """
        Get test run by ID, including state on all children
        """
        path_params = {"id": str(id)}

        return self.api_client.request(
            type_=m.TestRunExecutionWithChildren,
            method="GET",
            url="/api/v1/test_run_executions/{id}",
            path_params=path_params,
        )

    def _build_for_read_test_run_executions_api_v1_test_run_executions_get(
        self,
        project_id: Optional[int] = None,
        archived: Optional[bool] = None,
        search_query: Optional[str] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Awaitable[List[m.TestRunExecutionWithStats]]:
        """
        Retrieve test runs, including statistics.  Args:     project_id: Filter test runs by project.     archived: Get archived test runs, when true will return archived         test runs only, when false only non-archived test runs are returned.     skip: Pagination offset.     limit: Max number of records to return.  Returns:     List of test runs with execution statistics.
        """
        query_params = {}
        if project_id is not None:
            query_params["project_id"] = str(project_id)
        if archived is not None:
            query_params["archived"] = str(archived)
        if search_query is not None:
            query_params["search_query"] = str(search_query)
        if skip is not None:
            query_params["skip"] = str(skip)
        if limit is not None:
            query_params["limit"] = str(limit)

        return self.api_client.request(
            type_=List[m.TestRunExecutionWithStats],
            method="GET",
            url="/api/v1/test_run_executions/",
            params=query_params,
        )

    def _build_for_remove_test_run_execution_api_v1_test_run_executions_id_delete(
        self, id: int
    ) -> Awaitable[m.TestRunExecutionInDBBase]:
        """
        Remove test run execution
        """
        path_params = {"id": str(id)}

        return self.api_client.request(
            type_=m.TestRunExecutionInDBBase,
            method="DELETE",
            url="/api/v1/test_run_executions/{id}",
            path_params=path_params,
        )

    def _build_for_start_test_run_execution_api_v1_test_run_executions_id_start_post(
        self, id: int
    ) -> Awaitable[m.TestRunExecutionWithChildren]:
        """
        Start a test run by ID
        """
        path_params = {"id": str(id)}

        return self.api_client.request(
            type_=m.TestRunExecutionWithChildren,
            method="POST",
            url="/api/v1/test_run_executions/{id}/start",
            path_params=path_params,
        )

    def _build_for_unarchive_api_v1_test_run_executions_id_unarchive_post(
        self, id: int
    ) -> Awaitable[m.TestRunExecution]:
        """
        Unarchive test run execution by id.  Args:     id (int): test run execution id  Raises:     HTTPException: if no test run execution exists for provided id  Returns:     TestRunExecution: test run execution record that was unarchived
        """
        path_params = {"id": str(id)}

        return self.api_client.request(
            type_=m.TestRunExecution,
            method="POST",
            url="/api/v1/test_run_executions/{id}/unarchive",
            path_params=path_params,
        )

    def _build_for_upload_file_api_v1_test_run_executions_file_upload_post(self, file: IO[Any]) -> Awaitable[m.Any]:
        """
        Upload a file to the specified path of the current test run.  Args:     file: The file to upload.
        """
        files: Dict[str, IO[Any]] = {}  # noqa F841
        data: Dict[str, Any] = {}  # noqa F841
        files["file"] = file

        return self.api_client.request(
            type_=m.Any, method="POST", url="/api/v1/test_run_executions/file_upload/", data=data, files=files
        )


class AsyncTestRunExecutionsApi(_TestRunExecutionsApi):
    async def abort_testing_api_v1_test_run_executions_abort_testing_post(
        self,
    ) -> Dict[str, str]:
        """
        Cancel the current testing
        """
        return await self._build_for_abort_testing_api_v1_test_run_executions_abort_testing_post()

    async def archive_api_v1_test_run_executions_id_archive_post(self, id: int) -> m.TestRunExecution:
        """
        Archive test run execution by id.  Args:     id (int): test run execution id  Raises:     HTTPException: if no test run execution exists for provided id  Returns:     TestRunExecution: test run execution record that was archived
        """
        return await self._build_for_archive_api_v1_test_run_executions_id_archive_post(id=id)

    async def create_test_run_execution_api_v1_test_run_executions_post(
        self,
        body_create_test_run_execution_api_v1_test_run_executions_post: m.BodyCreateTestRunExecutionApiV1TestRunExecutionsPost,
    ) -> m.TestRunExecutionWithChildren:
        """
        Create new test run execution.
        """
        return await self._build_for_create_test_run_execution_api_v1_test_run_executions_post(
            body_create_test_run_execution_api_v1_test_run_executions_post=body_create_test_run_execution_api_v1_test_run_executions_post
        )

    async def download_log_api_v1_test_run_executions_id_log_get(
        self, id: int, json_entries: Optional[bool] = None, download: Optional[bool] = None
    ) -> None:
        """
        Download the logs from a test run.   Args:     id (int): Id of the TestRunExectution the log is requested for     json_entries (bool, optional): When set, return each log line as a json object     download (bool, optional): When set, return as attachment
        """
        return await self._build_for_download_log_api_v1_test_run_executions_id_log_get(
            id=id, json_entries=json_entries, download=download
        )

    async def get_test_runner_status_api_v1_test_run_executions_status_get(
        self,
    ) -> m.TestRunnerStatus:
        """
        Retrieve status of the Test Engine.  When the Test Engine is actively running the status will include the current test_run and the details of the states.
        """
        return await self._build_for_get_test_runner_status_api_v1_test_run_executions_status_get()

    async def read_test_run_execution_api_v1_test_run_executions_id_get(
        self, id: int
    ) -> m.TestRunExecutionWithChildren:
        """
        Get test run by ID, including state on all children
        """
        return await self._build_for_read_test_run_execution_api_v1_test_run_executions_id_get(id=id)

    async def read_test_run_executions_api_v1_test_run_executions_get(
        self,
        project_id: Optional[int] = None,
        archived: Optional[bool] = None,
        search_query: Optional[str] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[m.TestRunExecutionWithStats]:
        """
        Retrieve test runs, including statistics.  Args:     project_id: Filter test runs by project.     archived: Get archived test runs, when true will return archived         test runs only, when false only non-archived test runs are returned.     skip: Pagination offset.     limit: Max number of records to return.  Returns:     List of test runs with execution statistics.
        """
        return await self._build_for_read_test_run_executions_api_v1_test_run_executions_get(
            project_id=project_id, archived=archived, search_query=search_query, skip=skip, limit=limit
        )

    async def remove_test_run_execution_api_v1_test_run_executions_id_delete(
        self, id: int
    ) -> m.TestRunExecutionInDBBase:
        """
        Remove test run execution
        """
        return await self._build_for_remove_test_run_execution_api_v1_test_run_executions_id_delete(id=id)

    async def start_test_run_execution_api_v1_test_run_executions_id_start_post(
        self, id: int
    ) -> m.TestRunExecutionWithChildren:
        """
        Start a test run by ID
        """
        return await self._build_for_start_test_run_execution_api_v1_test_run_executions_id_start_post(id=id)

    async def unarchive_api_v1_test_run_executions_id_unarchive_post(self, id: int) -> m.TestRunExecution:
        """
        Unarchive test run execution by id.  Args:     id (int): test run execution id  Raises:     HTTPException: if no test run execution exists for provided id  Returns:     TestRunExecution: test run execution record that was unarchived
        """
        return await self._build_for_unarchive_api_v1_test_run_executions_id_unarchive_post(id=id)

    async def upload_file_api_v1_test_run_executions_file_upload_post(self, file: IO[Any]) -> m.Any:
        """
        Upload a file to the specified path of the current test run.  Args:     file: The file to upload.
        """
        return await self._build_for_upload_file_api_v1_test_run_executions_file_upload_post(file=file)


class SyncTestRunExecutionsApi(_TestRunExecutionsApi):
    def abort_testing_api_v1_test_run_executions_abort_testing_post(
        self,
    ) -> Dict[str, str]:
        """
        Cancel the current testing
        """
        coroutine = self._build_for_abort_testing_api_v1_test_run_executions_abort_testing_post()
        return get_event_loop().run_until_complete(coroutine)

    def archive_api_v1_test_run_executions_id_archive_post(self, id: int) -> m.TestRunExecution:
        """
        Archive test run execution by id.  Args:     id (int): test run execution id  Raises:     HTTPException: if no test run execution exists for provided id  Returns:     TestRunExecution: test run execution record that was archived
        """
        coroutine = self._build_for_archive_api_v1_test_run_executions_id_archive_post(id=id)
        return get_event_loop().run_until_complete(coroutine)

    def create_test_run_execution_api_v1_test_run_executions_post(
        self,
        body_create_test_run_execution_api_v1_test_run_executions_post: m.BodyCreateTestRunExecutionApiV1TestRunExecutionsPost,
    ) -> m.TestRunExecutionWithChildren:
        """
        Create new test run execution.
        """
        coroutine = self._build_for_create_test_run_execution_api_v1_test_run_executions_post(
            body_create_test_run_execution_api_v1_test_run_executions_post=body_create_test_run_execution_api_v1_test_run_executions_post
        )
        return get_event_loop().run_until_complete(coroutine)

    def download_log_api_v1_test_run_executions_id_log_get(
        self, id: int, json_entries: Optional[bool] = None, download: Optional[bool] = None
    ) -> None:
        """
        Download the logs from a test run.   Args:     id (int): Id of the TestRunExectution the log is requested for     json_entries (bool, optional): When set, return each log line as a json object     download (bool, optional): When set, return as attachment
        """
        coroutine = self._build_for_download_log_api_v1_test_run_executions_id_log_get(
            id=id, json_entries=json_entries, download=download
        )
        return get_event_loop().run_until_complete(coroutine)

    def get_test_runner_status_api_v1_test_run_executions_status_get(
        self,
    ) -> m.TestRunnerStatus:
        """
        Retrieve status of the Test Engine.  When the Test Engine is actively running the status will include the current test_run and the details of the states.
        """
        coroutine = self._build_for_get_test_runner_status_api_v1_test_run_executions_status_get()
        return get_event_loop().run_until_complete(coroutine)

    def read_test_run_execution_api_v1_test_run_executions_id_get(self, id: int) -> m.TestRunExecutionWithChildren:
        """
        Get test run by ID, including state on all children
        """
        coroutine = self._build_for_read_test_run_execution_api_v1_test_run_executions_id_get(id=id)
        return get_event_loop().run_until_complete(coroutine)

    def read_test_run_executions_api_v1_test_run_executions_get(
        self,
        project_id: Optional[int] = None,
        archived: Optional[bool] = None,
        search_query: Optional[str] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[m.TestRunExecutionWithStats]:
        """
        Retrieve test runs, including statistics.  Args:     project_id: Filter test runs by project.     archived: Get archived test runs, when true will return archived         test runs only, when false only non-archived test runs are returned.     skip: Pagination offset.     limit: Max number of records to return.  Returns:     List of test runs with execution statistics.
        """
        coroutine = self._build_for_read_test_run_executions_api_v1_test_run_executions_get(
            project_id=project_id, archived=archived, search_query=search_query, skip=skip, limit=limit
        )
        return get_event_loop().run_until_complete(coroutine)

    def remove_test_run_execution_api_v1_test_run_executions_id_delete(self, id: int) -> m.TestRunExecutionInDBBase:
        """
        Remove test run execution
        """
        coroutine = self._build_for_remove_test_run_execution_api_v1_test_run_executions_id_delete(id=id)
        return get_event_loop().run_until_complete(coroutine)

    def start_test_run_execution_api_v1_test_run_executions_id_start_post(
        self, id: int
    ) -> m.TestRunExecutionWithChildren:
        """
        Start a test run by ID
        """
        coroutine = self._build_for_start_test_run_execution_api_v1_test_run_executions_id_start_post(id=id)
        return get_event_loop().run_until_complete(coroutine)

    def unarchive_api_v1_test_run_executions_id_unarchive_post(self, id: int) -> m.TestRunExecution:
        """
        Unarchive test run execution by id.  Args:     id (int): test run execution id  Raises:     HTTPException: if no test run execution exists for provided id  Returns:     TestRunExecution: test run execution record that was unarchived
        """
        coroutine = self._build_for_unarchive_api_v1_test_run_executions_id_unarchive_post(id=id)
        return get_event_loop().run_until_complete(coroutine)

    def upload_file_api_v1_test_run_executions_file_upload_post(self, file: IO[Any]) -> m.Any:
        """
        Upload a file to the specified path of the current test run.  Args:     file: The file to upload.
        """
        coroutine = self._build_for_upload_file_api_v1_test_run_executions_file_upload_post(file=file)
        return get_event_loop().run_until_complete(coroutine)
