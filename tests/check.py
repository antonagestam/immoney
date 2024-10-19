from collections.abc import Callable
from collections.abc import Iterable
from typing import Any
from typing import Final
from typing import Generic

from typing_extensions import TypeVar

T = TypeVar("T", default=object)


class Check(Generic[T]):
    def __init__(
        self,
        required_type: Any,
        predicate: Callable[[T], bool],
    ) -> None:
        self.required_type: Final = required_type
        self.predicate: Final = predicate

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.required_type):
            return NotImplemented
        return self.predicate(other)


def sorted_items_equal(test: Iterable[T]) -> Check[Iterable[T]]:
    def check(other: Iterable[T]) -> bool:
        return sorted(other) == sorted(test)  # type: ignore[type-var]

    return Check(Iterable, check)
