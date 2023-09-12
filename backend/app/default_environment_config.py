from pathlib import Path

from app.schemas.test_environment_config import TestEnvironmentConfig

PROJECT_ROOT = Path(__file__).parent.parent
TEST_ENVIRONMENT_CONFIG_NAME = "default_test_environment.config"
TEST_ENVIRONMENT_CONFIG_PATH = PROJECT_ROOT / TEST_ENVIRONMENT_CONFIG_NAME

if not TEST_ENVIRONMENT_CONFIG_PATH.is_file():
    raise RuntimeError("No test environment config found. Recreating from example.")

default_environment_config = TestEnvironmentConfig.parse_file(
    TEST_ENVIRONMENT_CONFIG_PATH
)

default_environment_config.__dict__
