from __future__ import annotations

from decimal import Decimal
from fractions import Fraction

from typing import Sequence, Generic, TypeVar, overload, Final
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Currency:
    code: str
    numeric: str | None
    sub_unit: int = 1

    name: str | None = None
    countries: Sequence[str] | None = None


C = TypeVar("C", bound=Currency)


class Money(Generic[C]):
    __slots__ = ("value", "currency", "__weakref__")

    def __init__(self, value: Decimal | int | str, currency: Currency | str) -> None:
        self.value: Final = value
        self.currency: Final = currency

    @overload
    def __truediv__(self, other: int) -> tuple[Money[C], ...]: ...
    @overload
    def __truediv__(self, other: object) -> NotImplemented: ...
    def __truediv__(self, other: object) -> tuple[Money[C], ...]:
        """
        Divides the original value over the numerator and returns a tuple of new
        Money instances where the original value is spread as evenly as possible. The
        sum of the returned values will always equal the orignal value.

        >>> Money(3, "SEK") / 3
        (Money("1.00", "SEK"), Money("1.00", "SEK"), Money("1.00", "SEK"))
        >>> Money(3, "SEK") / 2
        (Money("1.50", "SEK"), Money("1.50", "SEK"))
        >>> Money("0.03", "SEK") / 2
        (Money("0.02", "SEK"), Money("0.01", "SEK"))
        """
        if not isinstance(other, int):
            return NotImplemented
        # TODO
        raise NotImplementedError
        return ()

    @overload
    def __floordiv__(self, other: int) -> MoneyFraction[C]: ...
    @overload
    def __floordiv__(self, other: object) -> NotImplemented: ...
    def __floordiv__(self, other: object) -> MoneyFraction[C]:
        if not isinstance(other, int):
            return NotImplemented
        return MoneyFraction(Fraction(self.value, other), self.currency)


class MoneyFraction(Generic[C]):
    __slots__ = ("value", "currency", "__weakref__")

    def __init__(self, value: Fraction, currency: Currency) -> None:
        self.value: Final = value
        self.currency: Final = currency
