import inspect

from api_lib_autogen import models
from api_lib_autogen.api_client import ApiClient, AsyncApis, SyncApis  # noqa F401
from pydantic import BaseModel

for model in inspect.getmembers(models, inspect.isclass):
    if model[1].__module__ == "api_lib_autogen.models":
        model_class = model[1]
        if issubclass(model_class, BaseModel):
            model_class.update_forward_refs()
