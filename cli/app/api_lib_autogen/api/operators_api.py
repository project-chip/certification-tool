# flake8: noqa E501
from asyncio import get_event_loop
from typing import TYPE_CHECKING, Awaitable, List, Optional

from api_lib_autogen import models as m
from fastapi.encoders import jsonable_encoder

if TYPE_CHECKING:
    from api_lib_autogen.api_client import ApiClient


class _OperatorsApi:
    def __init__(self, api_client: "ApiClient"):
        self.api_client = api_client

    def _build_for_create_operator_api_v1_operators_post(
        self, operator_create: m.OperatorCreate
    ) -> Awaitable[m.Operator]:
        """
        Create new operator.  Args:     operator_in (OperatorCreate): Parameters for new operator.  Returns:     Operator: newly created operator record
        """
        body = jsonable_encoder(operator_create)

        return self.api_client.request(type_=m.Operator, method="POST", url="/api/v1/operators/", json=body)

    def _build_for_delete_operator_api_v1_operators_id_delete(self, id: int) -> Awaitable[m.Operator]:
        """
        Lookup operator by id.  Args:     id (int): operator id  Raises:     HTTPException: if no operator exists for provided operator id  Returns:     Operator: operator record that was deleted
        """
        path_params = {"id": str(id)}

        return self.api_client.request(
            type_=m.Operator,
            method="DELETE",
            url="/api/v1/operators/{id}",
            path_params=path_params,
        )

    def _build_for_read_operator_api_v1_operators_id_get(self, id: int) -> Awaitable[m.Operator]:
        """
        Lookup operator by id.  Args:     id (int): operator id  Raises:     HTTPException: if no operator exists for provided operator id  Returns:     Operator: operator record
        """
        path_params = {"id": str(id)}

        return self.api_client.request(
            type_=m.Operator,
            method="GET",
            url="/api/v1/operators/{id}",
            path_params=path_params,
        )

    def _build_for_read_operators_api_v1_operators_get(
        self, skip: Optional[int] = None, limit: Optional[int] = None
    ) -> Awaitable[List[m.Operator]]:
        """
        Retrive list of operators.  Args:     skip (int, optional): Pagination offset. Defaults to 0.     limit (int, optional): max number of records to return. Defaults to 100.  Returns:     List[Operator]: List of operators
        """
        query_params = {}
        if skip is not None:
            query_params["skip"] = str(skip)
        if limit is not None:
            query_params["limit"] = str(limit)

        return self.api_client.request(
            type_=List[m.Operator],
            method="GET",
            url="/api/v1/operators/",
            params=query_params,
        )

    def _build_for_update_operator_api_v1_operators_id_put(
        self, id: int, operator_update: m.OperatorUpdate
    ) -> Awaitable[m.Operator]:
        """
        Update an existing operator.  Args:     id (int): operator id     operator_in (schemas.OperatorUpdate): operators parameters to be updated  Raises:     HTTPException: if no operator exists for provided operator id  Returns:     Operator: updated operator record
        """
        path_params = {"id": str(id)}

        body = jsonable_encoder(operator_update)

        return self.api_client.request(
            type_=m.Operator,
            method="PUT",
            url="/api/v1/operators/{id}",
            path_params=path_params,
            json=body,
        )


class AsyncOperatorsApi(_OperatorsApi):
    async def create_operator_api_v1_operators_post(self, operator_create: m.OperatorCreate) -> m.Operator:
        """
        Create new operator.  Args:     operator_in (OperatorCreate): Parameters for new operator.  Returns:     Operator: newly created operator record
        """
        return await self._build_for_create_operator_api_v1_operators_post(operator_create=operator_create)

    async def delete_operator_api_v1_operators_id_delete(self, id: int) -> m.Operator:
        """
        Lookup operator by id.  Args:     id (int): operator id  Raises:     HTTPException: if no operator exists for provided operator id  Returns:     Operator: operator record that was deleted
        """
        return await self._build_for_delete_operator_api_v1_operators_id_delete(id=id)

    async def read_operator_api_v1_operators_id_get(self, id: int) -> m.Operator:
        """
        Lookup operator by id.  Args:     id (int): operator id  Raises:     HTTPException: if no operator exists for provided operator id  Returns:     Operator: operator record
        """
        return await self._build_for_read_operator_api_v1_operators_id_get(id=id)

    async def read_operators_api_v1_operators_get(
        self, skip: Optional[int] = None, limit: Optional[int] = None
    ) -> List[m.Operator]:
        """
        Retrive list of operators.  Args:     skip (int, optional): Pagination offset. Defaults to 0.     limit (int, optional): max number of records to return. Defaults to 100.  Returns:     List[Operator]: List of operators
        """
        return await self._build_for_read_operators_api_v1_operators_get(skip=skip, limit=limit)

    async def update_operator_api_v1_operators_id_put(self, id: int, operator_update: m.OperatorUpdate) -> m.Operator:
        """
        Update an existing operator.  Args:     id (int): operator id     operator_in (schemas.OperatorUpdate): operators parameters to be updated  Raises:     HTTPException: if no operator exists for provided operator id  Returns:     Operator: updated operator record
        """
        return await self._build_for_update_operator_api_v1_operators_id_put(id=id, operator_update=operator_update)


class SyncOperatorsApi(_OperatorsApi):
    def create_operator_api_v1_operators_post(self, operator_create: m.OperatorCreate) -> m.Operator:
        """
        Create new operator.  Args:     operator_in (OperatorCreate): Parameters for new operator.  Returns:     Operator: newly created operator record
        """
        coroutine = self._build_for_create_operator_api_v1_operators_post(operator_create=operator_create)
        return get_event_loop().run_until_complete(coroutine)

    def delete_operator_api_v1_operators_id_delete(self, id: int) -> m.Operator:
        """
        Lookup operator by id.  Args:     id (int): operator id  Raises:     HTTPException: if no operator exists for provided operator id  Returns:     Operator: operator record that was deleted
        """
        coroutine = self._build_for_delete_operator_api_v1_operators_id_delete(id=id)
        return get_event_loop().run_until_complete(coroutine)

    def read_operator_api_v1_operators_id_get(self, id: int) -> m.Operator:
        """
        Lookup operator by id.  Args:     id (int): operator id  Raises:     HTTPException: if no operator exists for provided operator id  Returns:     Operator: operator record
        """
        coroutine = self._build_for_read_operator_api_v1_operators_id_get(id=id)
        return get_event_loop().run_until_complete(coroutine)

    def read_operators_api_v1_operators_get(
        self, skip: Optional[int] = None, limit: Optional[int] = None
    ) -> List[m.Operator]:
        """
        Retrive list of operators.  Args:     skip (int, optional): Pagination offset. Defaults to 0.     limit (int, optional): max number of records to return. Defaults to 100.  Returns:     List[Operator]: List of operators
        """
        coroutine = self._build_for_read_operators_api_v1_operators_get(skip=skip, limit=limit)
        return get_event_loop().run_until_complete(coroutine)

    def update_operator_api_v1_operators_id_put(self, id: int, operator_update: m.OperatorUpdate) -> m.Operator:
        """
        Update an existing operator.  Args:     id (int): operator id     operator_in (schemas.OperatorUpdate): operators parameters to be updated  Raises:     HTTPException: if no operator exists for provided operator id  Returns:     Operator: updated operator record
        """
        coroutine = self._build_for_update_operator_api_v1_operators_id_put(id=id, operator_update=operator_update)
        return get_event_loop().run_until_complete(coroutine)
