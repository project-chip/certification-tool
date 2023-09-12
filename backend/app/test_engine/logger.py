from loguru import logger

# Create logger wrapper with `test_run_log` in log record `extra`
test_engine_logger = logger.bind(test_run_log=True)

# Add custom logger for "chip-tool"
CHIPTOOL_LEVEL = "CHIPTOOL"
test_engine_logger.level(CHIPTOOL_LEVEL, no=21, icon="🤖", color="<cyan>")

# Log format for logs that come from CHIP. Arguments: module (e.g. "DMG"), message
CHIP_LOG_FORMAT = "CHIP:{} {}"
