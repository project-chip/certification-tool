from asyncio import Event, TimeoutError, wait_for
from typing import Any, Dict, List, Optional

from fastapi import WebSocket
from loguru import logger
from pydantic import ValidationError

from app.constants.websockets_constants import (
    MESSAGE_ID_KEY,
    MessageKeysEnum,
    MessageTypeEnum,
)
from app.singleton import Singleton
from app.socket_connection_manager import socket_connection_manager
from app.user_prompt_support.constants import (
    RESPONSE_KEY,
    STATUS_CODE_KEY,
    UserResponseStatusEnum,
)

from .prompt_request import PromptRequest
from .prompt_response import PromptResponse


# TODO: Rename the user prompt folder
# Class used as a transport wrapper to the PromptRequest PromptResponse objects
# exchanged between the websocket clients
class PromptExchange(object):
    def __init__(self, prompt: PromptRequest, message_id: int) -> None:
        self.message_id = message_id
        self.prompt = prompt
        self.message_event = Event()
        self.received_response: Optional[PromptResponse]

    def as_dictionary(self) -> Dict[MessageKeysEnum, Any]:
        prompt_dict = self.prompt.dict()
        prompt_dict[MESSAGE_ID_KEY] = self.message_id
        message_dict = {
            MessageKeysEnum.TYPE: MessageTypeEnum.PROMPT_REQUEST,
            MessageKeysEnum.PAYLOAD: prompt_dict,
        }
        return message_dict

    # Called from the prompt manager asynchronously when we receive a message
    def handle_response(self, message_dict: Dict[str, Any]) -> None:
        # Create and set a response object from  the message dictionary
        self.__set_response_for_message(message_dict)

        # TODO: Log the response
        self.message_event.set()

    # Waits for either of two conditions to happen:
    #   1. A response from the user for the prompt request, calls the response handler
    #   2. Timeout expires, sets the response as timedout, calls the timeout handler
    async def response(self) -> Optional[PromptResponse]:
        try:
            timeout = self.prompt.timeout
            await wait_for(self.message_event.wait(), timeout)
        except TimeoutError:
            await self.__handle_timeout()
        return self.received_response

    # Called internally when the timeout expires
    async def __handle_timeout(self) -> None:
        # Notify all connections of the timeout
        await user_prompt_manager.prompt_timed_out(prompt_exchange=self)

        # Create and set timeout response
        self.__set_response_for_status(UserResponseStatusEnum.TIMEOUT)

    def __set_response_for_status(self, status: UserResponseStatusEnum) -> None:
        self.received_response = PromptResponse(status_code=status)

    def __set_response_for_message(self, message_dict: Dict) -> None:
        # Ensure its a valid response
        try:
            self.received_response = PromptResponse(**message_dict)
        except ValidationError as error:
            # TODO: Log the error
            # Set invalid response
            self.__set_response_for_status(UserResponseStatusEnum.INVALID)
            logger.info(error.json())


# User Prompt Manager does the following functions:
#   - Register with socket connection manager to handle Prompt Response type messages
#   - Manage Timeouts and notifications for User Prompts
#   - Formats the Prompt objects to send and receive messages over websockets using an
#   intermediate class: PromptExchange
class UserPromptManager(object, metaclass=Singleton):
    def __init__(self) -> None:
        self.active_prompts: List[PromptExchange] = []
        self.__current_message_id = 0
        self.__current_prompt_exchange: Optional[PromptExchange] = None
        socket_connection_manager.register_handler(
            callback=self.received_message, message_type=MessageTypeEnum.PROMPT_RESPONSE
        )

    @property
    def current_message_id(self) -> int:
        self.__current_message_id += 1
        return self.__current_message_id

    @property
    def current_prompt_exchange(self) -> Optional[PromptExchange]:
        return self.__current_prompt_exchange

    def select_prompt_option(
        self, prompt_exchange: PromptExchange, option: int
    ) -> None:
        message = self.__select_option_message(prompt_exchange, option)
        self.received_message(message, None)

    async def send_prompt_request(
        self, prompt: PromptRequest
    ) -> Optional[PromptResponse]:
        self.__current_prompt_exchange = self.__create_prompt_exchange_for_prompt(
            prompt
        )
        await self.__send_prompt_exchange(self.__current_prompt_exchange)

        # Start timer and wait for a response or a timeout
        return await self.__current_prompt_exchange.response()

    def received_message(self, message_dict: Dict, socket: Optional[WebSocket]) -> None:
        if MESSAGE_ID_KEY not in message_dict:
            logger.info("Response dictionary missing the key for message_id")
            return

        # Fetch the message id
        response_message_id = message_dict[MESSAGE_ID_KEY]
        if response_message_id is None:
            # TODO: Log Error
            logger.info(
                "Message ID not found in response dictionary " + str(message_dict)
            )
            return

        # Find the user prompt using the message id and the list of active prompts
        prompt_exchange = self.__prompt_exchange_for_message(response_message_id)
        if prompt_exchange is None:
            # TODO: Log Error
            logger.info("User prompt not found, messageID:" + str(response_message_id))
            return

        self.active_prompts.remove(prompt_exchange)
        prompt_exchange.handle_response(message_dict=message_dict)

    async def prompt_timed_out(self, prompt_exchange: PromptExchange) -> None:
        try:
            self.active_prompts.remove(prompt_exchange)
        except ValueError as e:
            logger.info(
                "Prompt exchange not found, messageID:"
                + str(prompt_exchange.message_id)
            )
            raise (e)
        # Broadcast to all connections that we timed out and don't need the response
        message = self.__timeout_broadcast_message(prompt_exchange=prompt_exchange)
        await self.__send_message(message)

    async def __send_message(self, message: dict) -> None:
        await socket_connection_manager.broadcast(message)

    async def __send_prompt_exchange(self, prompt_exchange: PromptExchange) -> None:
        self.active_prompts.append(prompt_exchange)

        # Broadcast it to all connections
        await self.__send_message(prompt_exchange.as_dictionary())

    def __select_option_message(
        self, prompt_exchange: PromptExchange, option: int
    ) -> Dict[str, Any]:
        return {
            RESPONSE_KEY: option,
            STATUS_CODE_KEY: UserResponseStatusEnum.OKAY,
            MESSAGE_ID_KEY: prompt_exchange.message_id,
        }

    def __timeout_broadcast_message(
        self, prompt_exchange: PromptExchange
    ) -> Dict[MessageKeysEnum, Any]:
        # Create a timeout notification
        return {
            MessageKeysEnum.TYPE: MessageTypeEnum.TIME_OUT_NOTIFICATION,
            MessageKeysEnum.PAYLOAD: {MESSAGE_ID_KEY: prompt_exchange.message_id},
        }

    def __create_prompt_exchange_for_prompt(
        self, prompt: PromptRequest
    ) -> PromptExchange:
        return PromptExchange(prompt=prompt, message_id=self.current_message_id)

    def __prompt_exchange_for_message(
        self, message_id: Any
    ) -> Optional[PromptExchange]:
        return next(
            (
                prompt_exchange
                for prompt_exchange in self.active_prompts
                if prompt_exchange.message_id == message_id
            ),
            None,
        )


user_prompt_manager = UserPromptManager()
