# Ignore mypy type check for this file

# Need to figure out how to properly test chip-tool with the new WebSocketRunner.
# from unittest import mock

# import pytest

# from app.chip_tool import ChipTool
# from app.chip_tool.chip_tool import (
#     CHIP_TOOL_EXE,
#     PICS_FILE_PATH,
#     SHELL_OPTION,
#     SHELL_PATH,
#     ChipToolNotRunning,
#     ChipToolTestType,
# )
# from app.chip_tool.exec_run_in_container import ExecResultExtended
# from app.container_manager import container_manager
# from app.core.config import settings
# from app.schemas.pics import PICS, PICSError
# from app.tests.utils.docker import make_fake_container
# from app.tests.utils.test_pics_data import create_random_pics


# @pytest.mark.asyncio
# @mock.patch.object(target=ChipTool(), attribute="is_running", return_value=False)
# @mock.patch.object(container_manager, "create_container")
# async def test_chip_tool_start_container(mock_create_container, *_) -> None:
#     chip_tool = ChipTool()
#     test_type = ChipToolTestType.CHIP_TOOL

#     # Values to verify
#     docker_image = f"{settings.SDK_DOCKER_IMAGE}:{settings.SDK_DOCKER_TAG}"

#     await chip_tool.start_container(test_type)

#     mock_create_container.assert_called_once_with(docker_image,
#     ChipTool.run_parameters)

#     # clean up:
#     chip_tool._ChipTool__chip_tool_container = None


# @pytest.mark.asyncio
# @mock.patch.object(target=ChipTool(), attribute="is_running", return_value=True)
# @mock.patch.object(target=container_manager, attribute="destroy")
# @mock.patch.object(container_manager, "create_container")
# async def test_chip_tool_not_start_container_when_running(
#     mock_create_container,
#     *_,
# ) -> None:
#     chip_tool = ChipTool()
#     test_type = ChipToolTestType.CHIP_TOOL

#     await chip_tool.start_container(test_type)

#     mock_create_container.assert_not_called()

#     # clean up:
#     chip_tool._ChipTool__chip_tool_container = None


# @pytest.mark.asyncio
# @mock.patch.object(target=ChipTool(), attribute="is_running", return_value=False)
# @mock.patch.object(container_manager, "create_container")
# @mock.patch.object(target=container_manager, attribute="destroy")
# async def test_chip_tool_destroy_container_running(mock_destroy, *_) -> None:
#     chip_tool = ChipTool()
#     test_type = ChipToolTestType.CHIP_TOOL

#     await chip_tool.start_container(test_type)

#     chip_tool.destroy_device()
#     mock_destroy.assert_called()

#     # clean up:
#     chip_tool._ChipTool__chip_tool_container = None


# @pytest.mark.asyncio
# @mock.patch.object(target=container_manager, attribute="destroy")
# async def test_chip_tool_destroy_container_not_running(mock_destroy) -> None:
#     chip_tool = ChipTool()

#     chip_tool.destroy_device()
#     mock_destroy.assert_not_called()

#     # clean up:
#     chip_tool._ChipTool__chip_tool_container = None


# @pytest.mark.asyncio
# @mock.patch.object(target=ChipTool(), attribute="is_running", return_value=False)
# @mock.patch.object(container_manager, "create_container")
# @mock.patch.object(target=container_manager, attribute="destroy")
# async def test_chip_tool_destroy_container_once(
#     mock_destroy,
#     mock_create_container,
#     *_,
# ) -> None:
#     chip_tool = ChipTool()
#     test_type = ChipToolTestType.CHIP_TOOL

#     # Mock return values
#     mock_create_container.return_value = make_fake_container()

#     await chip_tool.start_container(test_type)

#     chip_tool.destroy_device()
#     chip_tool.destroy_device()
#     mock_destroy.assert_called_once()

#     # clean up:
#     chip_tool._ChipTool__chip_tool_container = None


# def test_chip_tool_send_command_without_starting() -> None:
#     chip_tool = ChipTool()

#     with pytest.raises(ChipToolNotRunning):
#         chip_tool.send_command("--help", prefix=CHIP_TOOL_EXE)

#     # clean up:
#     chip_tool._ChipTool__chip_tool_container = None


# @pytest.mark.asyncio
# @mock.patch.object(target=ChipTool(), attribute="is_running", return_value=False)
# @mock.patch.object(target=container_manager, attribute="destroy")
# @mock.patch.object(target=ChipTool(), attribute="last_command_exit_code")
# @mock.patch.object(container_manager, "create_container")
# @mock.patch("app.chip_tool.chip_tool.exec_run_in_container")
# async def test_chip_tool_set_pics(
#     mock_exec_run,
#     mock_create_container,
#     mock_last_command_exit_code,
#     *_,
# ) -> None:
#     chip_tool = ChipTool()
#     test_type = ChipToolTestType.CHIP_TOOL

#     # Mock return values
#     mock_last_command_exit_code.return_value = 0
#     mock_create_container.return_value = fake_container = make_fake_container()
#     mock_exec_run.return_value = ExecResultExtended(
#         0, "log output".encode(), "ID", mock.MagicMock()
#     )

#     await chip_tool.start_container(test_type)

#     pics: PICS = create_random_pics()
#     chip_tool.set_pics(pics=pics)

#     # expected PICS = PICS from create_random_pics() + \n + DEFAULT PICS
#     expected_pics_data = (
#         "AB.C=1\nAB.C.A0004=1\nXY.C=0\nAB.S.C0003=1\n"
#         "PICS_SDK_CI_ONLY=0\nPICS_SKIP_SAMPLE_APP=1\n"
#         "PICS_USER_PROMPT=1"
#     )
#     mock_exec_run.assert_called_once_with(
#         fake_container,
#         cmd=[
#             SHELL_PATH,
#             SHELL_OPTION,
#             f"echo '{expected_pics_data}' > {PICS_FILE_PATH}",
#         ],
#     )

#     assert chip_tool._ChipTool__pics_file_created is True
#     mock_exec_run.reset_mock()


# def test_chip_tool_set_pics_with_error() -> None:
#    return_value = ExecResultExtended(0, "log output".encode(), "ID", mock.MagicMock())

#     chip_tool = ChipTool()
#     fake_container = make_fake_container()
#     with mock.patch.object(
#         target=container_manager,
#         attribute="create_container",
#         return_value=fake_container,
#     ) as _, mock.patch.object(
#         target=chip_tool,
#         attribute="last_command_exit_code",
#         return_value=1,
#     ) as _, mock.patch(
#         "app.chip_tool.chip_tool.exec_run_in_container", return_value=return_value
#     ) as _:
#         try:
#             pics: PICS = create_random_pics()
#             chip_tool.set_pics(pics=pics)
#             assert False
#         except Exception as e:
#             assert isinstance(e, PICSError)


# @pytest.mark.asyncio
# @mock.patch.object(target=ChipTool(), attribute="is_running", return_value=False)
# @mock.patch.object(target=container_manager, attribute="destroy")
# @mock.patch.object(container_manager, "create_container")
# @mock.patch("app.chip_tool.chip_tool.exec_run_in_container")
# async def test_chip_tool_send_commands(
#     mock_exec_run,
#     mock_create_container,
#     *_,
# ) -> None:
#     # We need to control some core settings, as they can impact
#     # behavior being validated in this test.
#     #
#     # Current settings values are cached and reset and end of test case
#     original_trace_setting_value = settings.CHIP_TOOL_TRACE
#     if original_trace_setting_value is True:
#         settings.CHIP_TOOL_TRACE = False

#     # Attributes
#     chip_tool = ChipTool()
#     chip_tool_prefix = CHIP_TOOL_EXE
#     test_id = "TC_TEST_ID"
#     test_timeout = "900"

#     # Mock return values
#     mock_create_container.return_value = fake_container = make_fake_container()
#     mock_exec_run.return_value = ExecResultExtended(
#         0, "log output".encode(), "ID", mock.MagicMock()
#     )

#     await chip_tool.start_container()

#     # Send command default prefix
#     cmd = "--help"
#     chip_tool.send_command(cmd, prefix=CHIP_TOOL_EXE)
#     mock_exec_run.assert_called_once_with(
#         fake_container,
#         f"{chip_tool_prefix} {cmd}",
#         socket=False,
#         stream=False,
#         stdin=True,
#     )
#     mock_exec_run.reset_mock()

#     # Send command default custom prefix
#     custom_prefix = "cat"
#     chip_tool.send_command(cmd, prefix=custom_prefix)
#     mock_exec_run.assert_called_once_with(
#         fake_container,
#         f"{custom_prefix} {cmd}",
#         socket=False,
#         stream=False,
#         stdin=True,
#     )
#     mock_exec_run.reset_mock()

#     # Send run test for CHIP_TOOL with custom timeout
#     chip_tool.run_test(
#         test_id=test_id, test_type=ChipToolTestType.CHIP_TOOL, timeout=test_timeout
#     )
#     mock_exec_run.assert_called_once()
#     # command is 2nd parameter to first call in exec_run_in_container
#     command = mock_exec_run.mock_calls[0].args[1]
#     assert f"--timeout {test_timeout}" in command
#     mock_exec_run.reset_mock()

#     # Send run test for CHIP_TOOL with test parameters
#     test_param_name = "param1"
#     test_param_value = "value"
#     chip_tool.run_test(
#         test_id=test_id,
#         test_type=ChipToolTestType.CHIP_TOOL,
#         test_parameters={test_param_name: test_param_value},
#     )
#     mock_exec_run.assert_called_once()
#     # command is 2nd parameter to first call in exec_run_in_container
#     command = mock_exec_run.mock_calls[0].args[1]
#     assert f"--{test_param_name} {test_param_value}" in command
#     mock_exec_run.reset_mock()

#     # Send run test for CHIP_TOOL with test parameters which has empty strings
#     test_param_name = "param1"
#     test_param_value = ""
#     chip_tool.run_test(
#         test_id=test_id,
#         test_type=ChipToolTestType.CHIP_TOOL,
#         test_parameters={test_param_name: test_param_value},
#     )
#     mock_exec_run.assert_called_once()
#     # command is 2nd parameter to first call in exec_run_in_container
#     command = mock_exec_run.mock_calls[0].args[1]
#     assert f'--{test_param_name} ""' in command
#     mock_exec_run.reset_mock()

#     # Send run test for CHIP_TOOL with test_parameters skipping custom nodeID
#     chip_tool.run_test(
#         test_id=test_id,
#         test_type=ChipToolTestType.CHIP_TOOL,
#         test_parameters={
#             test_param_name: test_param_value,
#             "nodeId": "custom",
#             "cluster": "custom",
#         },
#     )
#     mock_exec_run.assert_called_once()
#     # command is 2nd parameter to first call in exec_run_in_container
#     command = mock_exec_run.mock_calls[0].args[1]
#     assert f"--{test_param_name} {test_param_value}" in command
#     assert "--nodeId custom" not in command
#     assert "--cluster custom" not in command
#     mock_exec_run.reset_mock()

#     test_name = "Test_TC_DM_1_3"
#     port = 5540
#     chip_tool.run_simulated_app_test(test_id=test_name, device_port=port)
#     mock_exec_run.assert_called_once_with(
#         fake_container,
#         f"./chip-app1 --command {test_name}_Simulated --secured-device-port {port}",
#         socket=True,
#         stream=False,
#         stdin=True,
#     )

#     # clean up:
#     chip_tool._ChipTool__chip_tool_container = None
#     settings.CHIP_TOOL_TRACE = original_trace_setting_value


# @pytest.mark.asyncio
# @mock.patch.object(target=ChipTool(), attribute="is_running", return_value=False)
# @mock.patch.object(target=container_manager, attribute="destroy")
# @mock.patch.object(container_manager, "create_container")
# @mock.patch("app.chip_tool.chip_tool.exec_run_in_container")
# async def test_set_paa_certs_with_pairing_on_network_expect_path(
#     mock_exec_run,
#     mock_create_container,
#     *_,
# ) -> None:
#     original_trace_setting_value = settings.CHIP_TOOL_TRACE
#     if original_trace_setting_value is True:
#         settings.CHIP_TOOL_TRACE = False

#     # Attributes
#     chip_tool = ChipTool()
#     chip_tool_prefix = CHIP_TOOL_EXE
#     discriminator = "1234"
#     setup_code = "0123456"
#     stream = False

#     # Mock return values
#     mock_create_container.return_value = fake_container = make_fake_container()
#     mock_exec_run.return_value = ExecResultExtended(
#         0, "log output".encode(), "ID", mock.MagicMock()
#     )

#     await chip_tool.start_container()

#     expected_params = f"{setup_code} {discriminator}"
#     expected_server_paa_params = (
#         f"{CHIP_TOOL_SERVER_ARGS_ARGNAME} "
#         f"'{CHIP_TOOL_SERVER_DEFAULT_ARGS} "
#         f"{CHIP_TOOL_PAA_CERTS_PATH_ARGNAME} {DOCKER_PAA_CERTS_PATH}'"
#     )
#     expected_command = (
#         f"{chip_tool_prefix} pairing onnetwork-long "
#         f"{hex(chip_tool.node_id)} {expected_params} "
#         f"{expected_server_paa_params}"
#     )

#     # Send on-network pairing command
#     chip_tool.pairing_on_network(
#         setup_code=setup_code,
#         discriminator=discriminator,
#         use_paa_certs=True,
#         stream=stream,
#     )

#     mock_exec_run.assert_called_once_with(
#         fake_container, expected_command, socket=False, stream=stream, stdin=True
#     )

#     # clean up:
#     chip_tool._ChipTool__chip_tool_container = None
#     settings.CHIP_TOOL_TRACE = original_trace_setting_value


# @pytest.mark.asyncio
# @mock.patch.object(target=ChipTool(), attribute="is_running", return_value=False)
# @mock.patch.object(target=container_manager, attribute="destroy")
# @mock.patch.object(container_manager, "create_container")
# @mock.patch("app.chip_tool.chip_tool.exec_run_in_container")
# async def test_set_paa_certs_with_pairing_ble_wifi_expect_path(
#     mock_exec_run,
#     mock_create_container,
#     *_,
# ) -> None:
#     original_trace_setting_value = settings.CHIP_TOOL_TRACE
#     if original_trace_setting_value is True:
#         settings.CHIP_TOOL_TRACE = False

#     # Attributes
#     chip_tool = ChipTool()
#     chip_tool_prefix = CHIP_TOOL_EXE
#     discriminator = "1234"
#     setup_code = "0123456"
#     ssid = "WifiIsGood"
#     password = "WifiIsGoodAndSecret"
#     stream = True

#     # Mock return values
#     mock_create_container.return_value = fake_container = make_fake_container()
#     mock_exec_run.return_value = ExecResultExtended(
#         0, "log output".encode(), "ID", mock.MagicMock()
#     )

#     await chip_tool.start_container()

#     expected_params = (
#         f"{hex(chip_tool.node_id)} {ssid} {password} {setup_code} {discriminator}"
#     )
#     expected_server_paa_params = (
#         f"{CHIP_TOOL_SERVER_ARGS_ARGNAME} "
#         f"'{CHIP_TOOL_SERVER_DEFAULT_ARGS} "
#         f"{CHIP_TOOL_PAA_CERTS_PATH_ARGNAME} {DOCKER_PAA_CERTS_PATH}'"
#     )
#     expected_command = (
#         f"{chip_tool_prefix} pairing ble-wifi {expected_params} "
#         f"{expected_server_paa_params}"
#     )

#     # Send BLE-WIFI pairing command
#     chip_tool.pairing_ble_wifi(
#         ssid=ssid,
#         password=password,
#         setup_code=setup_code,
#         discriminator=discriminator,
#         use_paa_certs=True,
#         stream=stream,
#     )

#     mock_exec_run.assert_called_once_with(
#         fake_container, expected_command, socket=False, stream=stream, stdin=True
#     )

#     # clean up:
#     chip_tool._ChipTool__chip_tool_container = None
#     settings.CHIP_TOOL_TRACE = original_trace_setting_value


# @pytest.mark.asyncio
# @mock.patch.object(target=ChipTool(), attribute="is_running", return_value=False)
# @mock.patch.object(target=container_manager, attribute="destroy")
# @mock.patch.object(container_manager, "create_container")
# @mock.patch("app.chip_tool.chip_tool.exec_run_in_container")
# async def test_set_paa_certs_with_pairing_ble_thread_expect_path(
#     mock_exec_run,
#     mock_create_container,
#     *_,
# ) -> None:
#     original_trace_setting_value = settings.CHIP_TOOL_TRACE
#     if original_trace_setting_value is True:
#         settings.CHIP_TOOL_TRACE = False

#     # Attributes
#     chip_tool = ChipTool()
#     chip_tool_prefix = CHIP_TOOL_EXE
#     discriminator = "1234"
#     hex_dataset = "c0ffee"
#     setup_code = "0123456"
#     stream = False

#     # Mock return values
#     mock_create_container.return_value = fake_container = make_fake_container()
#     mock_exec_run.return_value = ExecResultExtended(
#         0, "log output".encode(), "ID", mock.MagicMock()
#     )

#     await chip_tool.start_container()

#     expected_params = (
#         f"{hex(chip_tool.node_id)} hex:{hex_dataset} {setup_code} {discriminator}"
#     )
#     expected_server_paa_params = (
#         f"{CHIP_TOOL_SERVER_ARGS_ARGNAME} "
#         f"'{CHIP_TOOL_SERVER_DEFAULT_ARGS} "
#         f"{CHIP_TOOL_PAA_CERTS_PATH_ARGNAME} {DOCKER_PAA_CERTS_PATH}'"
#     )
#     expected_command = (
#         f"{chip_tool_prefix} pairing ble-thread {expected_params} "
#         f"{expected_server_paa_params}"
#     )

#     # Send BLE-THREAD pairing command
#     chip_tool.pairing_ble_thread(
#         hex_dataset=hex_dataset,
#         setup_code=setup_code,
#         discriminator=discriminator,
#         use_paa_certs=True,
#         stream=stream,
#     )

#     mock_exec_run.assert_called_once_with(
#         fake_container, expected_command, socket=False, stream=stream, stdin=True
#     )

#     # clean up:
#     chip_tool._ChipTool__chip_tool_container = None
#     settings.CHIP_TOOL_TRACE = original_trace_setting_value


# @pytest.mark.asyncio
# @mock.patch.object(target=ChipTool(), attribute="is_running", return_value=False)
# @mock.patch.object(target=container_manager, attribute="destroy")
# @mock.patch.object(container_manager, "create_container")
# @mock.patch("app.chip_tool.chip_tool.exec_run_in_container")
# async def test_clear_paa_certs_with_pairing_on_network_expect_no_path(
#     mock_exec_run,
#     mock_create_container,
#     *_,
# ) -> None:
#     original_trace_setting_value = settings.CHIP_TOOL_TRACE
#     if original_trace_setting_value is True:
#         settings.CHIP_TOOL_TRACE = False

#     # Attributes
#     chip_tool = ChipTool()
#     chip_tool_prefix = CHIP_TOOL_EXE
#     discriminator = "1234"
#     setup_code = "0123456"
#     stream = True

#     # Mock return values
#     mock_create_container.return_value = fake_container = make_fake_container()
#     mock_exec_run.return_value = ExecResultExtended(
#         0, "log output".encode(), "ID", mock.MagicMock()
#     )

#     await chip_tool.start_container()

#     expected_params = f"{hex(chip_tool.node_id)} {setup_code} {discriminator}"
#     expected_command = f"{chip_tool_prefix} pairing onnetwork-long {expected_params}"

#     # Send on-network pairing command
#     chip_tool.pairing_on_network(
#         setup_code=setup_code,
#         discriminator=discriminator,
#         use_paa_certs=False,
#         stream=stream,
#     )

#     mock_exec_run.assert_called_once_with(
#         fake_container, expected_command, socket=False, stream=stream, stdin=True
#     )

#     # clean up:
#     chip_tool._ChipTool__chip_tool_container = None
#     settings.CHIP_TOOL_TRACE = original_trace_setting_value


# @pytest.mark.asyncio
# @mock.patch.object(target=ChipTool(), attribute="is_running", return_value=False)
# @mock.patch.object(target=container_manager, attribute="destroy")
# @mock.patch.object(container_manager, "create_container")
# @mock.patch("app.chip_tool.chip_tool.exec_run_in_container")
# async def test_clear_paa_certs_with_pairing_ble_wifi_expect_no_path(
#     mock_exec_run,
#     mock_create_container,
#     *_,
# ) -> None:
#     original_trace_setting_value = settings.CHIP_TOOL_TRACE
#     if original_trace_setting_value is True:
#         settings.CHIP_TOOL_TRACE = False

#     # Attributes
#     chip_tool = ChipTool()
#     chip_tool_prefix = CHIP_TOOL_EXE
#     discriminator = "1234"
#     setup_code = "0123456"
#     ssid = "WifiIsGood"
#     password = "WifiIsGoodAndSecret"
#     stream = False

#     # Mock return values
#     mock_create_container.return_value = fake_container = make_fake_container()
#     mock_exec_run.return_value = ExecResultExtended(
#         0, "log output".encode(), "ID", mock.MagicMock()
#     )

#     await chip_tool.start_container()

#     expected_params = (
#         f"{hex(chip_tool.node_id)} {ssid} {password} {setup_code} {discriminator}"
#     )
#     expected_command = f"{chip_tool_prefix} pairing ble-wifi {expected_params}"

#     # Send BLE-WIFI pairing command
#     chip_tool.pairing_ble_wifi(
#         ssid=ssid,
#         password=password,
#         setup_code=setup_code,
#         discriminator=discriminator,
#         use_paa_certs=False,
#         stream=stream,
#     )

#     mock_exec_run.assert_called_once_with(
#         fake_container, expected_command, socket=False, stream=stream, stdin=True
#     )

#     # clean up:
#     chip_tool._ChipTool__chip_tool_container = None
#     settings.CHIP_TOOL_TRACE = original_trace_setting_value


# @pytest.mark.asyncio
# @mock.patch.object(target=ChipTool(), attribute="is_running", return_value=False)
# @mock.patch.object(target=container_manager, attribute="destroy")
# @mock.patch.object(container_manager, "create_container")
# @mock.patch("app.chip_tool.chip_tool.exec_run_in_container")
# async def test_clear_paa_certs_with_pairing_ble_thread_expect_no_path(
#     mock_exec_run,
#     mock_create_container,
#     *_,
# ) -> None:
#     original_trace_setting_value = settings.CHIP_TOOL_TRACE
#     if original_trace_setting_value is True:
#         settings.CHIP_TOOL_TRACE = False

#     # Attributes
#     chip_tool = ChipTool()
#     chip_tool_prefix = CHIP_TOOL_EXE
#     discriminator = "1234"
#     hex_dataset = "c0ffee"
#     setup_code = "0123456"
#     stream = True

#     # Mock return values
#     mock_create_container.return_value = fake_container = make_fake_container()
#     mock_exec_run.return_value = ExecResultExtended(
#         0, "log output".encode(), "ID", mock.MagicMock()
#     )

#     await chip_tool.start_container()

#     expected_params = (
#         f"{hex(chip_tool.node_id)} hex:{hex_dataset} {setup_code} {discriminator}"
#     )
#     expected_command = f"{chip_tool_prefix} pairing ble-thread {expected_params}"

#     # Send BLE-THREAD pairing command
#     chip_tool.pairing_ble_thread(
#         hex_dataset=hex_dataset,
#         setup_code=setup_code,
#         discriminator=discriminator,
#         use_paa_certs=False,
#         stream=stream,
#     )

#     mock_exec_run.assert_called_once_with(
#         fake_container, expected_command, socket=False, stream=stream, stdin=True
#     )

#     # clean up:
#     chip_tool._ChipTool__chip_tool_container = None
#     settings.CHIP_TOOL_TRACE = original_trace_setting_value


# @pytest.mark.asyncio
# @mock.patch.object(target=ChipTool(), attribute="is_running", return_value=False)
# @mock.patch.object(target=container_manager, attribute="destroy")
# @mock.patch.object(container_manager, "create_container")
# @mock.patch("app.chip_tool.chip_tool.exec_run_in_container")
# async def test_set_paa_certs_with_run_test_expect_path(mock_exec_run, *_) -> None:
#     chip_tool = ChipTool()
#     chip_tool_prefix = CHIP_TOOL_EXE
#     test_id = "TC_TEST_ID"

#     # Mock return values
#     mock_exec_run.return_value = ExecResultExtended(
#         0, "log output".encode(), "ID", mock.MagicMock()
#     )

#     await chip_tool.start_container()

#     # Send run test for CHIP_TOOL with PAA certs set
#     chip_tool.run_test(
#         test_id=test_id, test_type=ChipToolTestType.CHIP_TOOL, use_paa_certs=True
#     )
#     mock_exec_run.assert_called_once()
#     # command is 2nd parameter to first call in exec_run_in_container
#     command = mock_exec_run.mock_calls[0].args[1]

#     # assert command arguments
#     assert f"{chip_tool_prefix} tests {test_id} " in command
#     assert f"--nodeId {hex(chip_tool.node_id)} " in command
#     assert f"--delayInMs {DELAY_VALUE} " in command
#     assert f"--continueOnFailure {CHIP_TOOL_CONTINUE_ON_FAILURE_VALUE}" in command
#     assert f"--timeout {CHIP_TOOL_TEST_DEFAULT_TIMEOUT_IN_SEC}" in command
#     assert f"{CHIP_TOOL_PAA_CERTS_PATH_ARGNAME} {DOCKER_PAA_CERTS_PATH}" in command

#     # clean up:
#     chip_tool._ChipTool__chip_tool_container = None


# @pytest.mark.asyncio
# @mock.patch.object(target=ChipTool(), attribute="is_running", return_value=False)
# @mock.patch.object(target=container_manager, attribute="destroy")
# @mock.patch.object(container_manager, "create_container")
# @mock.patch("app.chip_tool.chip_tool.exec_run_in_container")
# async def test_clear_paa_certs_with_run_test_expect_no_path(
#     mock_exec_run,
#     *_,
# ) -> None:
#     chip_tool = ChipTool()
#     chip_tool_prefix = CHIP_TOOL_EXE
#     test_id = "TC_TEST_ID"

#     # Mock return values
#     mock_exec_run.return_value = ExecResultExtended(
#         0, "log output".encode(), "ID", mock.MagicMock()
#     )

#     await chip_tool.start_container()

#     # Send run test for CHIP_TOOL with PAA certs set
#     chip_tool.run_test(
#         test_id=test_id, test_type=ChipToolTestType.CHIP_TOOL, use_paa_certs=False
#     )
#     mock_exec_run.assert_called_once()
#     # command is 2nd parameter to first call in exec_run_in_container
#     command = mock_exec_run.mock_calls[0].args[1]

#     # assert command arguments with PAA certificates path
#     assert f"{chip_tool_prefix} tests {test_id} " in command
#     assert f"--nodeId {hex(chip_tool.node_id)} " in command
#     assert f"--delayInMs {DELAY_VALUE} " in command
#     assert f"--continueOnFailure {CHIP_TOOL_CONTINUE_ON_FAILURE_VALUE}" in command
#     assert f"--timeout {CHIP_TOOL_TEST_DEFAULT_TIMEOUT_IN_SEC}" in command
#     assert f"{CHIP_TOOL_PAA_CERTS_PATH_ARGNAME} {DOCKER_PAA_CERTS_PATH}"
#     not in command

#     # clean up:
#     chip_tool._ChipTool__chip_tool_container = None
