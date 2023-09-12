import os

from config import config
from loguru import logger

# Add custom logger for "chip-tool"
CHIPTOOL_LEVEL = "CHIPTOOL"
logger.level(CHIPTOOL_LEVEL, no=21, icon="🤖", color="<cyan>")


def configure_logger_for_run(title: str) -> str:
    # Reset (Remove all sinks from logger)
    logger.remove()

    log_path = os.path.join(config.log_config.output_log_path, f"test_run_{title}.log")

    logger.add(log_path, enqueue=True, format=config.log_config.format)

    return log_path
