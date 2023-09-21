import json
from json import JSONDecodeError
from typing import Callable, Dict, List, Union

import pydantic
from fastapi import WebSocket
from loguru import logger
from starlette.websockets import WebSocketState
from websockets.exceptions import ConnectionClosedOK

from app.constants.websockets_constants import (
    INVALID_JSON_ERROR_STR,
    MISSING_TYPE_ERROR_STR,
    NO_HANDLER_FOR_MSG_ERROR_STR,
    MessageKeysEnum,
    MessageTypeEnum,
)
from app.singleton import Singleton

SocketMessageHander = Callable[[Dict, WebSocket], None]


# SocketConnectionManager manages and maintains all the active socket connections
# communicating with the tool:
#   - Handles all incoming and outgoing messages from the tool.
#   - Has a list of handlers that can register for specific message types to get
#   callbacks on those messages.
#   - Allows broadcasting as well sending personal messages to all or single client
class SocketConnectionManager(object, metaclass=Singleton):
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []
        self.__message_handlers: Dict[MessageTypeEnum, SocketMessageHander] = {}

    async def connect(self, websocket: WebSocket) -> None:
        try:
            await websocket.accept()
            logger.info(f'Websocket connected: "{websocket}".')
            self.active_connections.append(websocket)
        except RuntimeError as e:
            logger.info(f'Failed to connect with error: "{e}".')
            raise e

    def disconnect(self, websocket: WebSocket) -> None:
        logger.info(f'Websocket disconnected: "{websocket}".')
        self.active_connections.remove(websocket)

    async def send_personal_message(
        self, message: Union[str, dict, list], websocket: WebSocket
    ) -> None:
        # Convert dictionaries and lists to string using json
        if isinstance(message, dict) or isinstance(message, list):
            message = json.dumps(message)
        await websocket.send_text(message)

    async def broadcast(self, message: Union[str, dict, list]) -> None:
        # Convert dictionaries and lists to string using json
        if isinstance(message, dict) or isinstance(message, list):
            message = json.dumps(message, default=pydantic.json.pydantic_encoder)
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            # Starlette raises websockets.exceptions.ConnectionClosedOK when trying to
            # send to a closed socket. https://github.com/encode/starlette/issues/759
            except ConnectionClosedOK:
                if connection.application_state != WebSocketState.DISCONNECTED:
                    await connection.close()
                logger.warning(
                    f'Failed to send message: "{message}" to socket: "{connection}",'
                    "connection closed."
                )
            except RuntimeError as e:
                logger.warning(
                    f'Failed to send: "{message}" to socket: "{connection}."',
                    'Error:"{e}"',
                )
                raise e

    async def received_message(self, socket: WebSocket, message: str) -> None:
        try:
            json_dict = json.loads(message)
            await self.__handle_received_json(socket, json_dict)
        except JSONDecodeError:
            await self.__notify_invalid_message(
                socket=socket, message=INVALID_JSON_ERROR_STR
            )

    # Note: Currently we only support one message handler per type, registering the
    # handler will displace the previous handler(if any)
    def register_handler(
        self, callback: SocketMessageHander, message_type: MessageTypeEnum
    ) -> None:
        self.__message_handlers[message_type] = callback

    async def __handle_received_json(self, socket: WebSocket, json_dict: dict) -> None:
        message_type = json_dict[MessageKeysEnum.TYPE]
        if message_type is None:
            # Every message must have a type key for the tool to be able to route it
            await self.__notify_invalid_message(
                socket=socket, message=MISSING_TYPE_ERROR_STR
            )
            return

        if message_type not in self.__message_handlers.keys():
            # No handler registered for this type of message
            await self.__notify_invalid_message(
                socket=socket, message=NO_HANDLER_FOR_MSG_ERROR_STR
            )
            return

        message_handler = self.__message_handlers[message_type]
        message_handler(json_dict[MessageKeysEnum.PAYLOAD], socket)

    async def __notify_invalid_message(self, socket: WebSocket, message: str) -> None:
        notify_message = {
            MessageKeysEnum.TYPE: MessageTypeEnum.INVALID_MESSAGE,
            MessageKeysEnum.PAYLOAD: message,
        }
        await self.send_personal_message(message=notify_message, websocket=socket)


socket_connection_manager = SocketConnectionManager()
