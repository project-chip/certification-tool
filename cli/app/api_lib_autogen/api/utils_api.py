# flake8: noqa E501
from asyncio import get_event_loop
from typing import TYPE_CHECKING, Awaitable

from api_lib_autogen import models as m

if TYPE_CHECKING:
    from api_lib_autogen.api_client import ApiClient


class _UtilsApi:
    def __init__(self, api_client: "ApiClient"):
        self.api_client = api_client

    def _build_for_test_email_api_v1_utils_test_email_post(self, email_to: str) -> Awaitable[m.Msg]:
        """
        Test emails.
        """
        query_params = {"email_to": str(email_to)}

        return self.api_client.request(
            type_=m.Msg,
            method="POST",
            url="/api/v1/utils/test-email/",
            params=query_params,
        )


class AsyncUtilsApi(_UtilsApi):
    async def test_email_api_v1_utils_test_email_post(self, email_to: str) -> m.Msg:
        """
        Test emails.
        """
        return await self._build_for_test_email_api_v1_utils_test_email_post(email_to=email_to)


class SyncUtilsApi(_UtilsApi):
    def test_email_api_v1_utils_test_email_post(self, email_to: str) -> m.Msg:
        """
        Test emails.
        """
        coroutine = self._build_for_test_email_api_v1_utils_test_email_post(email_to=email_to)
        return get_event_loop().run_until_complete(coroutine)
