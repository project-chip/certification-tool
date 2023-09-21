from pathlib import Path
from shutil import copyfile

from pydantic import BaseModel


class LogConfig(BaseModel):
    output_log_path = "./run_logs"
    format = "<level>{level: <8}</level> | <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{message}</level>"


class Config(BaseModel):
    hostname = "localhost"
    log_config: LogConfig = LogConfig()


config_root = Path(__file__).parents[1]
config_file = Path.joinpath(config_root, "config.json")

# copy example file if no config file present
if not config_file.is_file():
    example_config_file = Path.joinpath(config_root, "config.json.example")
    copyfile(example_config_file, config_file)

config = Config.parse_file(config_file)
