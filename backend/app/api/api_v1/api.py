from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    devices,
    operators,
    projects,
    test_collections,
    test_harness_backend_version,
    test_run_configs,
    test_run_executions,
    utils,
)
from app.api.api_v1.sockets import web_sockets

api_router = APIRouter()
api_router.include_router(
    test_collections.router, prefix="/test_collections", tags=["test collections"]
)

api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(operators.router, prefix="/operators", tags=["operators"])
api_router.include_router(
    test_run_executions.router,
    prefix="/test_run_executions",
    tags=["test_run_executions"],
)
api_router.include_router(
    test_run_configs.router, prefix="/test_run_configs", tags=["test_run_configs"]
)

api_router.include_router(test_harness_backend_version.router, tags=["version"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(devices.router, prefix="/devices", tags=["devices"])

# Websocket API:
api_router.include_router(web_sockets.router)
