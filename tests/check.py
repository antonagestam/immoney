from typing import Callable, TypeVar, Final, Sequence, Generic, Iterable
from collections import Counter, defaultdict

T = TypeVar("T")

class Check(Generic[T]):
    def __init__(
        self,
        required_type: type[T],
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
        return sorted(other) == sorted(test)
    return Check(Iterable, check)
