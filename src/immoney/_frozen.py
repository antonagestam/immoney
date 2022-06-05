from typing_extensions import Never

from .errors import FrozenInstanceError


class Frozen:
    __slots__ = ("__weakref__",)

    # Using Never makes mypy give a type error for assignment to attributes (because
    # Never is the bottom type).
    def __setattr__(self, key: str, value: Never) -> None:
        if all(hasattr(self, attribute) for attribute in self.__slots__):
            raise FrozenInstanceError(
                f"Instances of {type(self).__qualname__!r} are immutable, cannot write "
                f"to attribute {key!r}"
            )
        super().__setattr__(key, value)
