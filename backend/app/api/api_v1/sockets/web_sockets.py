import asyncio

from fastapi import APIRouter, WebSocket
from fastapi.websockets import WebSocketDisconnect

from app.socket_connection_manager import SocketConnectionManager

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    socket_connection_manager = SocketConnectionManager()
    await socket_connection_manager.connect(websocket)
    try:
        while True:
            # WebSocketDisconnect is not raised unless we poll
            # https://github.com/tiangolo/fastapi/issues/3008
            try:
                message = await asyncio.wait_for(websocket.receive_text(), 0.1)
                await socket_connection_manager.received_message(
                    socket=websocket, message=message
                )
            except asyncio.TimeoutError:
                pass

    except WebSocketDisconnect:
        socket_connection_manager.disconnect(websocket)
