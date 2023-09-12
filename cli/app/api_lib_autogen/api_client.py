from asyncio import get_event_loop
from typing import Any, Awaitable, Callable, Dict, Generic, Optional, Type, TypeVar, overload

from api_lib_autogen.api.devices_api import AsyncDevicesApi, SyncDevicesApi
from api_lib_autogen.api.operators_api import AsyncOperatorsApi, SyncOperatorsApi
from api_lib_autogen.api.projects_api import AsyncProjectsApi, SyncProjectsApi
from api_lib_autogen.api.test_collections_api import AsyncTestCollectionsApi, SyncTestCollectionsApi
from api_lib_autogen.api.test_run_configs_api import AsyncTestRunConfigsApi, SyncTestRunConfigsApi
from api_lib_autogen.api.test_run_executions_api import AsyncTestRunExecutionsApi, SyncTestRunExecutionsApi
from api_lib_autogen.api.utils_api import AsyncUtilsApi, SyncUtilsApi
from api_lib_autogen.exceptions import ResponseHandlingException, UnexpectedResponse
from httpx import AsyncClient, Request, Response
from pydantic import ValidationError, parse_obj_as

ClientT = TypeVar("ClientT", bound="ApiClient")


class AsyncApis(Generic[ClientT]):
    def __init__(self, client: ClientT):
        self.client = client

        self.devices_api = AsyncDevicesApi(self.client)
        self.operators_api = AsyncOperatorsApi(self.client)
        self.projects_api = AsyncProjectsApi(self.client)
        self.test_collections_api = AsyncTestCollectionsApi(self.client)
        self.test_run_configs_api = AsyncTestRunConfigsApi(self.client)
        self.test_run_executions_api = AsyncTestRunExecutionsApi(self.client)
        self.utils_api = AsyncUtilsApi(self.client)


class SyncApis(Generic[ClientT]):
    def __init__(self, client: ClientT):
        self.client = client

        self.devices_api = SyncDevicesApi(self.client)
        self.operators_api = SyncOperatorsApi(self.client)
        self.projects_api = SyncProjectsApi(self.client)
        self.test_collections_api = SyncTestCollectionsApi(self.client)
        self.test_run_configs_api = SyncTestRunConfigsApi(self.client)
        self.test_run_executions_api = SyncTestRunExecutionsApi(self.client)
        self.utils_api = SyncUtilsApi(self.client)


T = TypeVar("T")
Send = Callable[[Request], Awaitable[Response]]
MiddlewareT = Callable[[Request, Send], Awaitable[Response]]


class ApiClient:
    def __init__(self, host: Optional[str] = None, **kwargs: Any) -> None:
        self.host = host
        self.middleware: MiddlewareT = BaseMiddleware()
        self._async_client = AsyncClient(**kwargs)

    async def aclose(self) -> None:
        await self._async_client.aclose()

    def close(self) -> None:
        get_event_loop().run_until_complete(self.aclose())

    @overload
    async def request(
        self, *, type_: Type[T], method: str, url: str, path_params: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> T:
        ...

    @overload  # noqa F811
    async def request(
        self, *, type_: None, method: str, url: str, path_params: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> None:
        ...

    async def request(  # noqa F811
        self, *, type_: Any, method: str, url: str, path_params: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Any:
        if path_params is None:
            path_params = {}
        url = (self.host or "") + url.format(**path_params)
        request = Request(method, url, **kwargs)
        return await self.send(request, type_)

    @overload
    def request_sync(self, *, type_: Type[T], **kwargs: Any) -> T:
        ...

    @overload  # noqa F811
    def request_sync(self, *, type_: None, **kwargs: Any) -> None:
        ...

    def request_sync(self, *, type_: Any, **kwargs: Any) -> Any:  # noqa F811
        """
        This method is not used by the generated apis, but is included for convenience
        """
        return get_event_loop().run_until_complete(self.request(type_=type_, **kwargs))

    async def send(self, request: Request, type_: Type[T]) -> T:
        response = await self.middleware(request, self.send_inner)
        if response.status_code in [200, 201]:
            try:
                return parse_obj_as(type_, response.json())
            except ValidationError as e:
                raise ResponseHandlingException(e)
        raise UnexpectedResponse.for_response(response)

    async def send_inner(self, request: Request) -> Response:
        try:
            response = await self._async_client.send(request)
        except Exception as e:
            raise ResponseHandlingException(e)
        return response

    def add_middleware(self, middleware: MiddlewareT) -> None:
        current_middleware = self.middleware

        async def new_middleware(request: Request, call_next: Send) -> Response:
            async def inner_send(request: Request) -> Response:
                return await current_middleware(request, call_next)

            return await middleware(request, inner_send)

        self.middleware = new_middleware


class BaseMiddleware:
    async def __call__(self, request: Request, call_next: Send) -> Response:
        return await call_next(request)
