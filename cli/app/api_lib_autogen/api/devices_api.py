# flake8: noqa E501
from asyncio import get_event_loop
from typing import TYPE_CHECKING, Any, Awaitable

from api_lib_autogen import models as m
from fastapi.encoders import jsonable_encoder

if TYPE_CHECKING:
    from api_lib_autogen.api_client import ApiClient


class _DevicesApi:
    def __init__(self, api_client: "ApiClient"):
        self.api_client = api_client

    def _build_for_add_device_config_api_v1_devices_put(self, body: Any) -> Awaitable[m.Any]:
        body = jsonable_encoder(body)

        return self.api_client.request(type_=m.Any, method="PUT", url="/api/v1/devices/", json=body)

    def _build_for_get_device_configs_api_v1_devices_get(
        self,
    ) -> Awaitable[m.Any]:
        return self.api_client.request(
            type_=m.Any,
            method="GET",
            url="/api/v1/devices/",
        )


class AsyncDevicesApi(_DevicesApi):
    async def add_device_config_api_v1_devices_put(self, body: Any) -> m.Any:
        return await self._build_for_add_device_config_api_v1_devices_put(body=body)

    async def get_device_configs_api_v1_devices_get(
        self,
    ) -> m.Any:
        return await self._build_for_get_device_configs_api_v1_devices_get()


class SyncDevicesApi(_DevicesApi):
    def add_device_config_api_v1_devices_put(self, body: Any) -> m.Any:
        coroutine = self._build_for_add_device_config_api_v1_devices_put(body=body)
        return get_event_loop().run_until_complete(coroutine)

    def get_device_configs_api_v1_devices_get(
        self,
    ) -> m.Any:
        coroutine = self._build_for_get_device_configs_api_v1_devices_get()
        return get_event_loop().run_until_complete(coroutine)
