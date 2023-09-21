from http import HTTPStatus

from fastapi.testclient import TestClient

from app.core.config import settings


def test_read_available_test_collections(client: TestClient) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/test_collections",
    )
    assert response.status_code == HTTPStatus.OK

    content = response.json()
    assert "test_collections" in content
    test_collections = content["test_collections"]
    assert "tool_unit_tests" in test_collections
    tool_unit_tests = test_collections["tool_unit_tests"]
    assert "test_suites" in tool_unit_tests
    test_suites = tool_unit_tests["test_suites"]
    assert "TestSuiteExpected" in test_suites
    test_suite_expected = test_suites["TestSuiteExpected"]
    assert "metadata" in test_suite_expected
