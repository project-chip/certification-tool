import asyncio
from functools import wraps

# We're ignoring type checking in this file as it is not currently supported in mypy:
# https://github.com/python/mypy/issues/4643


def async_cmd(f):  # type: ignore
    """This is a decorator that alow us to declare async click commands."""

    @wraps(f)
    def wrapper(*args, **kwargs):  # type: ignore
        return asyncio.run(f(*args, **kwargs))

    return wrapper
