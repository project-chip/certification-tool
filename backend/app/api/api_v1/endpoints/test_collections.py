from typing import Any

from fastapi import APIRouter

from app.schemas import TestCollections
from app.test_engine.test_script_manager import test_script_manager

router = APIRouter()


@router.get("/", response_model=TestCollections)
def read_test_collections() -> Any:
    """
    Retrieve available test collections.
    """

    return {
        "test_collections": {
            k: v.as_dict() for k, v in test_script_manager.test_collections.items()
        }
    }
