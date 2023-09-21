# flake8: noqa E501
from asyncio import get_event_loop
from typing import TYPE_CHECKING, Awaitable, List, Optional

from api_lib_autogen import models as m
from fastapi.encoders import jsonable_encoder

if TYPE_CHECKING:
    from api_lib_autogen.api_client import ApiClient


class _ProjectsApi:
    def __init__(self, api_client: "ApiClient"):
        self.api_client = api_client

    def _build_for_archive_project_api_v1_projects_id_archive_post(self, id: int) -> Awaitable[m.Project]:
        """
        Archive project by id.  Args:     id (int): project id  Raises:     HTTPException: if no project exists for provided project id  Returns:     Project: project record that was archived
        """
        path_params = {"id": str(id)}

        return self.api_client.request(
            type_=m.Project,
            method="POST",
            url="/api/v1/projects/{id}/archive",
            path_params=path_params,
        )

    def _build_for_create_project_api_v1_projects_post(self, project_create: m.ProjectCreate) -> Awaitable[m.Project]:
        """
        Create new project  Args:     project_in (ProjectCreate): Parameters for new project,  see schema for details  Returns:     Project: newly created project record
        """
        body = jsonable_encoder(project_create)

        return self.api_client.request(type_=m.Project, method="POST", url="/api/v1/projects/", json=body)

    def _build_for_default_config_api_v1_projects_default_config_get(
        self,
    ) -> Awaitable[m.TestEnvironmentConfig]:
        """
        Return default configuration for projects.  Returns:     List[Project]: List of projects
        """
        return self.api_client.request(
            type_=m.TestEnvironmentConfig,
            method="GET",
            url="/api/v1/projects/default_config",
        )

    def _build_for_delete_project_api_v1_projects_id_delete(self, id: int) -> Awaitable[m.Project]:
        """
        Delete project by id  Args:     id (int): project id  Raises:     HTTPException: if no project exists for provided project id  Returns:     Project: project record that was deleted
        """
        path_params = {"id": str(id)}

        return self.api_client.request(
            type_=m.Project,
            method="DELETE",
            url="/api/v1/projects/{id}",
            path_params=path_params,
        )

    def _build_for_read_project_api_v1_projects_id_get(self, id: int) -> Awaitable[m.Project]:
        """
        Lookup project by id  Args:     id (int): project id  Raises:     HTTPException: if no project exists for provided project id  Returns:     Project: project record
        """
        path_params = {"id": str(id)}

        return self.api_client.request(
            type_=m.Project,
            method="GET",
            url="/api/v1/projects/{id}",
            path_params=path_params,
        )

    def _build_for_read_projects_api_v1_projects_get(
        self, archived: Optional[bool] = None, skip: Optional[int] = None, limit: Optional[int] = None
    ) -> Awaitable[List[m.Project]]:
        """
        Retrive list of projects  Args:     archived (bool, optional): Get archived projects, when true will; get archived         projects only, when false only non-archived projects are returned.         Defaults to false.     skip (int, optional): Pagination offset. Defaults to 0.     limit (int, optional): max number of records to return. Defaults to 100.  Returns:     List[Project]: List of projects
        """
        query_params = {}
        if archived is not None:
            query_params["archived"] = str(archived)
        if skip is not None:
            query_params["skip"] = str(skip)
        if limit is not None:
            query_params["limit"] = str(limit)

        return self.api_client.request(
            type_=List[m.Project],
            method="GET",
            url="/api/v1/projects/",
            params=query_params,
        )

    def _build_for_unarchive_project_api_v1_projects_id_unarchive_post(self, id: int) -> Awaitable[m.Project]:
        """
        Unarchive project by id.  Args:     id (int): project id  Raises:     HTTPException: if no project exists for provided project id  Returns:     Project: project record that was unarchived
        """
        path_params = {"id": str(id)}

        return self.api_client.request(
            type_=m.Project,
            method="POST",
            url="/api/v1/projects/{id}/unarchive",
            path_params=path_params,
        )

    def _build_for_update_project_api_v1_projects_id_put(
        self, id: int, project_update: m.ProjectUpdate
    ) -> Awaitable[m.Project]:
        """
        Update an existing project  Args:     id (int): project id     project_in (schemas.ProjectUpdate): projects parameters to be updated  Raises:     HTTPException: if no project exists for provided project id  Returns:     Project: updated project record
        """
        path_params = {"id": str(id)}

        body = jsonable_encoder(project_update)

        return self.api_client.request(
            type_=m.Project, method="PUT", url="/api/v1/projects/{id}", path_params=path_params, json=body
        )


class AsyncProjectsApi(_ProjectsApi):
    async def archive_project_api_v1_projects_id_archive_post(self, id: int) -> m.Project:
        """
        Archive project by id.  Args:     id (int): project id  Raises:     HTTPException: if no project exists for provided project id  Returns:     Project: project record that was archived
        """
        return await self._build_for_archive_project_api_v1_projects_id_archive_post(id=id)

    async def create_project_api_v1_projects_post(self, project_create: m.ProjectCreate) -> m.Project:
        """
        Create new project  Args:     project_in (ProjectCreate): Parameters for new project,  see schema for details  Returns:     Project: newly created project record
        """
        return await self._build_for_create_project_api_v1_projects_post(project_create=project_create)

    async def default_config_api_v1_projects_default_config_get(
        self,
    ) -> m.TestEnvironmentConfig:
        """
        Return default configuration for projects.  Returns:     List[Project]: List of projects
        """
        return await self._build_for_default_config_api_v1_projects_default_config_get()

    async def delete_project_api_v1_projects_id_delete(self, id: int) -> m.Project:
        """
        Delete project by id  Args:     id (int): project id  Raises:     HTTPException: if no project exists for provided project id  Returns:     Project: project record that was deleted
        """
        return await self._build_for_delete_project_api_v1_projects_id_delete(id=id)

    async def read_project_api_v1_projects_id_get(self, id: int) -> m.Project:
        """
        Lookup project by id  Args:     id (int): project id  Raises:     HTTPException: if no project exists for provided project id  Returns:     Project: project record
        """
        return await self._build_for_read_project_api_v1_projects_id_get(id=id)

    async def read_projects_api_v1_projects_get(
        self, archived: Optional[bool] = None, skip: Optional[int] = None, limit: Optional[int] = None
    ) -> List[m.Project]:
        """
        Retrive list of projects  Args:     archived (bool, optional): Get archived projects, when true will; get archived         projects only, when false only non-archived projects are returned.         Defaults to false.     skip (int, optional): Pagination offset. Defaults to 0.     limit (int, optional): max number of records to return. Defaults to 100.  Returns:     List[Project]: List of projects
        """
        return await self._build_for_read_projects_api_v1_projects_get(archived=archived, skip=skip, limit=limit)

    async def unarchive_project_api_v1_projects_id_unarchive_post(self, id: int) -> m.Project:
        """
        Unarchive project by id.  Args:     id (int): project id  Raises:     HTTPException: if no project exists for provided project id  Returns:     Project: project record that was unarchived
        """
        return await self._build_for_unarchive_project_api_v1_projects_id_unarchive_post(id=id)

    async def update_project_api_v1_projects_id_put(self, id: int, project_update: m.ProjectUpdate) -> m.Project:
        """
        Update an existing project  Args:     id (int): project id     project_in (schemas.ProjectUpdate): projects parameters to be updated  Raises:     HTTPException: if no project exists for provided project id  Returns:     Project: updated project record
        """
        return await self._build_for_update_project_api_v1_projects_id_put(id=id, project_update=project_update)


class SyncProjectsApi(_ProjectsApi):
    def archive_project_api_v1_projects_id_archive_post(self, id: int) -> m.Project:
        """
        Archive project by id.  Args:     id (int): project id  Raises:     HTTPException: if no project exists for provided project id  Returns:     Project: project record that was archived
        """
        coroutine = self._build_for_archive_project_api_v1_projects_id_archive_post(id=id)
        return get_event_loop().run_until_complete(coroutine)

    def create_project_api_v1_projects_post(self, project_create: m.ProjectCreate) -> m.Project:
        """
        Create new project  Args:     project_in (ProjectCreate): Parameters for new project,  see schema for details  Returns:     Project: newly created project record
        """
        coroutine = self._build_for_create_project_api_v1_projects_post(project_create=project_create)
        return get_event_loop().run_until_complete(coroutine)

    def default_config_api_v1_projects_default_config_get(
        self,
    ) -> m.TestEnvironmentConfig:
        """
        Return default configuration for projects.  Returns:     List[Project]: List of projects
        """
        coroutine = self._build_for_default_config_api_v1_projects_default_config_get()
        return get_event_loop().run_until_complete(coroutine)

    def delete_project_api_v1_projects_id_delete(self, id: int) -> m.Project:
        """
        Delete project by id  Args:     id (int): project id  Raises:     HTTPException: if no project exists for provided project id  Returns:     Project: project record that was deleted
        """
        coroutine = self._build_for_delete_project_api_v1_projects_id_delete(id=id)
        return get_event_loop().run_until_complete(coroutine)

    def read_project_api_v1_projects_id_get(self, id: int) -> m.Project:
        """
        Lookup project by id  Args:     id (int): project id  Raises:     HTTPException: if no project exists for provided project id  Returns:     Project: project record
        """
        coroutine = self._build_for_read_project_api_v1_projects_id_get(id=id)
        return get_event_loop().run_until_complete(coroutine)

    def read_projects_api_v1_projects_get(
        self, archived: Optional[bool] = None, skip: Optional[int] = None, limit: Optional[int] = None
    ) -> List[m.Project]:
        """
        Retrive list of projects  Args:     archived (bool, optional): Get archived projects, when true will; get archived         projects only, when false only non-archived projects are returned.         Defaults to false.     skip (int, optional): Pagination offset. Defaults to 0.     limit (int, optional): max number of records to return. Defaults to 100.  Returns:     List[Project]: List of projects
        """
        coroutine = self._build_for_read_projects_api_v1_projects_get(archived=archived, skip=skip, limit=limit)
        return get_event_loop().run_until_complete(coroutine)

    def unarchive_project_api_v1_projects_id_unarchive_post(self, id: int) -> m.Project:
        """
        Unarchive project by id.  Args:     id (int): project id  Raises:     HTTPException: if no project exists for provided project id  Returns:     Project: project record that was unarchived
        """
        coroutine = self._build_for_unarchive_project_api_v1_projects_id_unarchive_post(id=id)
        return get_event_loop().run_until_complete(coroutine)

    def update_project_api_v1_projects_id_put(self, id: int, project_update: m.ProjectUpdate) -> m.Project:
        """
        Update an existing project  Args:     id (int): project id     project_in (schemas.ProjectUpdate): projects parameters to be updated  Raises:     HTTPException: if no project exists for provided project id  Returns:     Project: updated project record
        """
        coroutine = self._build_for_update_project_api_v1_projects_id_put(id=id, project_update=project_update)
        return get_event_loop().run_until_complete(coroutine)
