from typing import Any, Dict, Type


class Singleton(type):
    """This is a metaclass for declaring classes a singletons

    usage:
    ```
    class NewSingletonClass(baseClass, metaclass=Singleton):
    ```
    """

    _instances: Dict[Type, object] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> object:
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
