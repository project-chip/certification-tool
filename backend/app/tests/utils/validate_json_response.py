from typing import Any, Union

from httpx import Response as HTTPX_RESPONSE
from requests import Response


def validate_json_response(
    response: Union[Response, HTTPX_RESPONSE],
    expected_status_code: int,
    expected_content: dict[str, Any] = {},
    expected_keys: list[str] = [],
    dissalowed_keys: list[str] = [],
) -> None:
    """Utility to validate json response from API calls.

    Args:
        response: Full response object return from TestClient
        expected_status_code: Expected HTTP status code
        expected_content: Required content in JSON body. Validate that subset is present
            with exact values. Not recursive on nested dictionaries. Defaults to {}.
        expected_keys: Required keys in JSON body. Used to validate presense of fields,
            with any value. Defaults to [].
        dissalowed_keys: List of keys that are not allowed in the
            JSON body. Defaults to [].
    """

    assert response.status_code == expected_status_code
    content = response.json()

    for key in expected_content.keys():
        expected_value = expected_content[key]

        assert (
            key in content
        ), f"{key} missing in response JSON. Expected {key} to be {expected_value}."

        assert content[key] == expected_value

    for key in expected_keys:
        assert key in content, f"{key} missing in response JSON."

    for key in dissalowed_keys:
        assert key not in content, f"{key} not expected in response JSON."
