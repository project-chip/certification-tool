import asyncio
import json
import re
from typing import Any, Union

import aioconsole
import click

# from loguru import logger
from websockets.client import WebSocketClientProtocol

from .socket_schemas import (
    OptionsSelectPromptRequest,
    PromptRequest,
    PromptResponse,
    TextInputPromptRequest,
    UserResponseStatusEnum,
)


async def handle_prompt(socket: WebSocketClientProtocol, request: PromptRequest) -> None:
    click.echo("=======================================")
    if isinstance(request, OptionsSelectPromptRequest):
        await __handle_options_prompt(socket=socket, prompt=request)
    elif isinstance(request, TextInputPromptRequest):
        await __handle_text_prompt(socket=socket, prompt=request)
    else:
        click.echo(f"Unsupported prompt request: {request.__class__.__name__}")
    click.echo("=======================================")


async def __handle_options_prompt(socket: WebSocketClientProtocol, prompt: OptionsSelectPromptRequest) -> None:
    try:
        user_answer = await asyncio.wait_for(__prompt_user_for_option(prompt), float(prompt.timeout))
        await __send_prompt_response(socket=socket, input=user_answer, prompt=prompt)
    except asyncio.exceptions.TimeoutError:
        click.echo("Prompt timed out", err=True)
        pass


async def __prompt_user_for_option(prompt: OptionsSelectPromptRequest) -> int:
    # Print Prompt
    click.echo(prompt.prompt)
    for key in prompt.options.keys():
        id = prompt.options[key]
        click.echo(f"  {str(id)}: {key}")
    click.echo("Please enter a number for an option above: ")

    # Wait for input async
    input = await aioconsole.ainput()

    # validate input
    try:
        input_int = int(input)
        if input_int in prompt.options.values():
            return input_int
    except ValueError:
        pass

    # Recursively Retry
    await asyncio.sleep(0.1)
    click.echo(f"Invalid input {input}", err=True)
    return await __prompt_user_for_option(prompt)


async def __handle_text_prompt(socket: WebSocketClientProtocol, prompt: TextInputPromptRequest) -> None:
    try:
        user_answer = await asyncio.wait_for(__prompt_user_for_text_input(prompt), float(prompt.timeout))
        await __send_prompt_response(socket=socket, input=user_answer, prompt=prompt)
    except asyncio.exceptions.TimeoutError:
        click.echo("Prompt timed out", err=True)
        pass


async def __prompt_user_for_text_input(prompt: TextInputPromptRequest) -> str:
    # Print Prompt
    click.echo(prompt.prompt)

    # TODO: default value, placeholder.

    # Wait for input async
    input = await aioconsole.ainput()

    # validate input
    if __valid_text_input(input=input, prompt=prompt):
        return input

    # Recursively Retry
    await asyncio.sleep(0.1)
    click.echo(f"Invalid input {input}", err=True)
    return await __prompt_user_for_text_input(prompt)


def __valid_text_input(input: Any, prompt: TextInputPromptRequest) -> bool:
    if not isinstance(input, str):
        return False

    if prompt.regex_pattern is None:
        return True

    return re.match(prompt.regex_pattern, input) is not None


async def __send_prompt_response(
    socket: WebSocketClientProtocol, input: Union[str, int], prompt: PromptRequest
) -> None:
    response = PromptResponse(
        response=input,
        status_code=UserResponseStatusEnum.OKAY,
        message_id=prompt.message_id,
    )
    payload_dict = {
        "type": "prompt_response",
        "payload": response.dict(),
    }
    payload = json.dumps(payload_dict)
    await socket.send(payload)
