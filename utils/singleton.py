"""Singleton metaclass for use by registries and config loaders."""


class SingletonMeta(type):
    """Thread-safe singleton metaclass.

    Usage:
        class MyClass(metaclass=SingletonMeta):
            ...
    """

    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
