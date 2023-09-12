# flake8: noqa E501
from asyncio import get_event_loop
from typing import TYPE_CHECKING, Awaitable, List, Optional

from api_lib_autogen import models as m
from fastapi.encoders import jsonable_encoder

if TYPE_CHECKING:
    from api_lib_autogen.api_client import ApiClient


class _TestRunConfigsApi:
    def __init__(self, api_client: "ApiClient"):
        self.api_client = api_client

    def _build_for_create_test_run_config_api_v1_test_run_configs_post(
        self, test_run_config_create: m.TestRunConfigCreate
    ) -> Awaitable[m.TestRunConfig]:
        """
        Create new test run config.
        """
        body = jsonable_encoder(test_run_config_create)

        return self.api_client.request(type_=m.TestRunConfig, method="POST", url="/api/v1/test_run_configs/", json=body)

    def _build_for_read_test_run_config_api_v1_test_run_configs_id_get(self, id: int) -> Awaitable[m.TestRunConfig]:
        """
        Get test run config by ID.
        """
        path_params = {"id": str(id)}

        return self.api_client.request(
            type_=m.TestRunConfig,
            method="GET",
            url="/api/v1/test_run_configs/{id}",
            path_params=path_params,
        )

    def _build_for_read_test_run_configs_api_v1_test_run_configs_get(
        self, skip: Optional[int] = None, limit: Optional[int] = None
    ) -> Awaitable[List[m.TestRunConfig]]:
        """
        Retrieve test_run_configs.
        """
        query_params = {}
        if skip is not None:
            query_params["skip"] = str(skip)
        if limit is not None:
            query_params["limit"] = str(limit)

        return self.api_client.request(
            type_=List[m.TestRunConfig],
            method="GET",
            url="/api/v1/test_run_configs/",
            params=query_params,
        )

    def _build_for_update_test_run_config_api_v1_test_run_configs_id_put(
        self, id: int, test_run_config_update: m.TestRunConfigUpdate
    ) -> Awaitable[m.TestRunConfig]:
        """
        Update a test run config.
        """
        path_params = {"id": str(id)}

        body = jsonable_encoder(test_run_config_update)

        return self.api_client.request(
            type_=m.TestRunConfig, method="PUT", url="/api/v1/test_run_configs/{id}", path_params=path_params, json=body
        )


class AsyncTestRunConfigsApi(_TestRunConfigsApi):
    async def create_test_run_config_api_v1_test_run_configs_post(
        self, test_run_config_create: m.TestRunConfigCreate
    ) -> m.TestRunConfig:
        """
        Create new test run config.
        """
        return await self._build_for_create_test_run_config_api_v1_test_run_configs_post(
            test_run_config_create=test_run_config_create
        )

    async def read_test_run_config_api_v1_test_run_configs_id_get(self, id: int) -> m.TestRunConfig:
        """
        Get test run config by ID.
        """
        return await self._build_for_read_test_run_config_api_v1_test_run_configs_id_get(id=id)

    async def read_test_run_configs_api_v1_test_run_configs_get(
        self, skip: Optional[int] = None, limit: Optional[int] = None
    ) -> List[m.TestRunConfig]:
        """
        Retrieve test_run_configs.
        """
        return await self._build_for_read_test_run_configs_api_v1_test_run_configs_get(skip=skip, limit=limit)

    async def update_test_run_config_api_v1_test_run_configs_id_put(
        self, id: int, test_run_config_update: m.TestRunConfigUpdate
    ) -> m.TestRunConfig:
        """
        Update a test run config.
        """
        return await self._build_for_update_test_run_config_api_v1_test_run_configs_id_put(
            id=id, test_run_config_update=test_run_config_update
        )


class SyncTestRunConfigsApi(_TestRunConfigsApi):
    def create_test_run_config_api_v1_test_run_configs_post(
        self, test_run_config_create: m.TestRunConfigCreate
    ) -> m.TestRunConfig:
        """
        Create new test run config.
        """
        coroutine = self._build_for_create_test_run_config_api_v1_test_run_configs_post(
            test_run_config_create=test_run_config_create
        )
        return get_event_loop().run_until_complete(coroutine)

    def read_test_run_config_api_v1_test_run_configs_id_get(self, id: int) -> m.TestRunConfig:
        """
        Get test run config by ID.
        """
        coroutine = self._build_for_read_test_run_config_api_v1_test_run_configs_id_get(id=id)
        return get_event_loop().run_until_complete(coroutine)

    def read_test_run_configs_api_v1_test_run_configs_get(
        self, skip: Optional[int] = None, limit: Optional[int] = None
    ) -> List[m.TestRunConfig]:
        """
        Retrieve test_run_configs.
        """
        coroutine = self._build_for_read_test_run_configs_api_v1_test_run_configs_get(skip=skip, limit=limit)
        return get_event_loop().run_until_complete(coroutine)

    def update_test_run_config_api_v1_test_run_configs_id_put(
        self, id: int, test_run_config_update: m.TestRunConfigUpdate
    ) -> m.TestRunConfig:
        """
        Update a test run config.
        """
        coroutine = self._build_for_update_test_run_config_api_v1_test_run_configs_id_put(
            id=id, test_run_config_update=test_run_config_update
        )
        return get_event_loop().run_until_complete(coroutine)
