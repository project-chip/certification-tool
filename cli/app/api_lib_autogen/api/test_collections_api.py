# flake8: noqa E501
from asyncio import get_event_loop
from typing import TYPE_CHECKING, Awaitable

from api_lib_autogen import models as m

if TYPE_CHECKING:
    from api_lib_autogen.api_client import ApiClient


class _TestCollectionsApi:
    def __init__(self, api_client: "ApiClient"):
        self.api_client = api_client

    def _build_for_read_test_collections_api_v1_test_collections_get(
        self,
    ) -> Awaitable[m.TestCollections]:
        """
        Retrieve available test collections.
        """
        return self.api_client.request(
            type_=m.TestCollections,
            method="GET",
            url="/api/v1/test_collections/",
        )


class AsyncTestCollectionsApi(_TestCollectionsApi):
    async def read_test_collections_api_v1_test_collections_get(
        self,
    ) -> m.TestCollections:
        """
        Retrieve available test collections.
        """
        return await self._build_for_read_test_collections_api_v1_test_collections_get()


class SyncTestCollectionsApi(_TestCollectionsApi):
    def read_test_collections_api_v1_test_collections_get(
        self,
    ) -> m.TestCollections:
        """
        Retrieve available test collections.
        """
        coroutine = self._build_for_read_test_collections_api_v1_test_collections_get()
        return get_event_loop().run_until_complete(coroutine)
