from typing import Generator

from app.chip_tool.exec_run_in_container import exec_run_in_container
from app.tests.utils.docker import make_fake_container


def test_exec_run_in_container_not_stream() -> None:
    cmd = "fake command"
    exec_id = "1234567890ab"
    output_str = "log output"
    exit_code = 0

    container = make_fake_container(
        mock_api_config={
            "exec_create.return_value": {"Id": exec_id},
            "exec_start.return_value": output_str.encode(),
            "exec_inspect.return_value": {"ExitCode": exit_code},
        }
    )

    result = exec_run_in_container(container, cmd, stream=False)

    assert result.exit_code == exit_code
    assert isinstance(result.output, bytes)
    assert result.output.decode() == output_str
    assert result.exec_id == exec_id


def test_exec_run_in_container_stream() -> None:
    cmd = "fake command"
    exec_id = "1234567890ab"
    output_str = "log output"
    exit_code = 0
    output_gen = (s for s in [output_str])
    container = make_fake_container(
        mock_api_config={
            "exec_create.return_value": {"Id": exec_id},
            "exec_start.return_value": output_gen,
            "exec_inspect.return_value": {"ExitCode": exit_code},
        }
    )

    result = exec_run_in_container(container, cmd, stream=True)

    assert result.exit_code is None
    assert isinstance(result.output, Generator)
    assert result.exec_id == exec_id
