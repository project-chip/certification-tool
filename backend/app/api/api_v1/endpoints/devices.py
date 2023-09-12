from typing import Any

from fastapi import APIRouter
from loguru import logger

router = APIRouter()


@router.put("/", response_model=dict)
def add_device_config(deviceData: dict) -> Any:
    logger.info("New device request received : ", deviceData)
    return {"status": "Success"}


@router.get("/", response_model=dict)
def get_device_configs() -> Any:
    logger.info("fetch devices request received.")
    return [
        {
            "device": "Simple Bulb",
            "details": {
                "pid": "123",
                "vid": "135",
                "firmware_rev": "abc",
                "device_type": "type 1",
                "manufacturer": "Alex",
                "hid": "abc1.2",
            },
        },
        {
            "device": "Advanced Plug",
            "details": {
                "pid": "789",
                "vid": "579",
                "firmware_rev": "xyz",
                "device_type": "type 7",
                "manufacturer": "Nick",
                "hid": "xyz4.66",
            },
        },
    ]
