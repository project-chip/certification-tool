from api_lib_autogen.api_client import ApiClient
from config import config

client = ApiClient(host=f"http://{config.hostname}")
