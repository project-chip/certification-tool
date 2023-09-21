from asyncio.log import logger
from socket import SocketIO
from typing import Generator, NamedTuple, Optional, Union

from docker.errors import APIError
from docker.models.containers import Container
from docker.utils.socket import frames_iter


class ExecResultExtended(NamedTuple):
    """Extension of the ExecResult from docker, including the execution id."""

    exit_code: Optional[int]
    output: Union[Generator, bytes, tuple]
    exec_id: str
    socket: Union[SocketIO, None]


def exec_run_in_container(
    container: Container,
    cmd: Union[str, list],
    stdout: bool = True,
    stderr: bool = True,
    stdin: bool = False,
    tty: bool = False,
    privileged: bool = False,
    user: str = "",
    detach: bool = False,
    stream: bool = False,
    socket: bool = False,
    environment: Optional[Union[dict, list]] = None,
    workdir: Optional[str] = None,
    demux: bool = False,
) -> ExecResultExtended:
    """
    Run a command inside this container. Similar to
    ``docker exec``.

    NOTE: This is a modified version from the docker package, exposing the internal
    execution ID, enabling users of the API to retrieve information about the execution
    after it has finished. This is usefull for retrieving the exit code when streaming
    logs

    Args:
        cmd (str or list): Command to be executed
        stdout (bool): Attach to stdout. Default: ``True``
        stderr (bool): Attach to stderr. Default: ``True``
        stdin (bool): Attach to stdin. Default: ``False``
        tty (bool): Allocate a pseudo-TTY. Default: False
        privileged (bool): Run as privileged.
        user (str): User to execute command as. Default: root
        detach (bool): If true, detach from the exec command.
            Default: False
        stream (bool): Stream response data. Default: False
        socket (bool): Return the connection socket to allow custom
            read/write operations. Default: False
        environment (dict or list): A dictionary or a list of strings in
            the following format ``["PASSWORD=xxx"]`` or
            ``{"PASSWORD": "xxx"}``.
        workdir (str): Path to working directory for this exec session
        demux (bool): Return stdout and stderr separately

    Returns:
        (ExecResult): A tuple of (exit_code, output)
            exit_code: (int):
                Exit code for the executed command or ``None`` if
                either ``stream`` or ``socket`` is ``True``.
            output: (generator, bytes, or tuple):
                If ``stream=True``, a generator yielding response chunks.
                If ``socket=True``, a socket object for the connection.
                If ``demux=True``, a tuple of two bytes: stdout and stderr.
                A bytestring containing response data otherwise.

    Raises:
        :py:class:`docker.errors.APIError`
            If the server returns an error.
    """
    resp = container.client.api.exec_create(
        container.id,
        cmd,
        stdout=stdout,
        stderr=stderr,
        stdin=stdin,
        tty=tty,
        privileged=privileged,
        user=user,
        environment=environment,
        workdir=workdir,
    )
    exec_id = resp.get("Id")
    if exec_id is None:
        raise APIError("Docker API exec_create response doesn't contain execution id.")

    exec_output = container.client.api.exec_start(
        exec_id,
        detach=detach,
        tty=tty,
        stream=stream,
        socket=socket,
        demux=demux,
    )

    # If socket is True,
    #    - a socket object is returned by exec_start
    #    - use the socket object to retrieve the generator
    # If stream is True,
    #    - exec_start returns the generator
    sock = None
    if socket:
        sock = exec_output
        logger.info(f"#$#$ Data type is {type(sock)}")
        generator = read_generator_from_socket(socket=sock)
    elif stream:
        sock = None
        generator = exec_output

    # When using socket and stream options, the execution is non-blocking and we cannot
    # return the exit code
    if socket or stream:
        return ExecResultExtended(None, generator, exec_id, sock)

    # We get the execution exit code, we need inspect the execution using docker
    execution_metadata = container.client.api.exec_inspect(exec_id)
    if execution_metadata is None:
        raise APIError(
            f"Docker API exec_inspect didn't return metadata for id: {exec_id}."
        )
    exit_code = execution_metadata.get("ExitCode")

    return ExecResultExtended(exit_code, exec_output, exec_id, sock)


def read_generator_from_socket(socket: SocketIO, tty: bool = False) -> Generator:
    gen = frames_iter(socket, tty)
    # The generator will output strings
    generator = (data for (_, data) in gen)
    return generator
