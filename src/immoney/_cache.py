from collections.abc import Callable
from functools import lru_cache
from typing import Any


class InstanceCache(type):
    """
    A metaclass that caches instances using functools.lru_cache. Normalization is
    assumed to be deterministic and instances are cached by both raw input and their
    normalized counterparts.

    Concrete classes that use this metaclass must implement the static method
    `_normalize`.
    """

    _normalize: Callable[..., tuple[object, ...]]

    @lru_cache
    def __instantiate(cls, *args: object) -> object:
        return super().__call__(*args)

    def __call__(cls, *args: object, **kwargs: object) -> Any:
        return cls.__instantiate(*cls._normalize(*args, **kwargs))
