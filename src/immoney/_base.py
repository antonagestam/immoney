from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import ROUND_DOWN
from decimal import Decimal
from fractions import Fraction
from functools import cached_property
from itertools import chain
from typing import Final, Literal
from typing import Generic
from typing import TypeVar
from typing import overload

from typing_extensions import Self

from src.immoney.errors import MoneyParseError

from ._types import PositiveDecimal


@dataclass(frozen=True)
class Currency:
    code: str
    # numeric: str | None
    subunit: int = 1

    # name: str | None = None
    # countries: Sequence[str] | None = None

    def __str__(self) -> str:
        return self.code

    @cached_property
    def decimal_exponent(self) -> Decimal:
        # Is there a smarter way to do this?
        return Decimal("0." + int(math.log10(self.subunit)) * "0")

    @cached_property
    def zero(self: Self) -> Money[Self]:
        return Money(0, self)

    @cached_property
    def one_subunit(self) -> Money[Self]:
        return Money

    def normalize_value(self, value: Decimal | int | str) -> PositiveDecimal:
        try:
            positive = PositiveDecimal.parse(value)
        except (TypeError, ValueError) as e:
            raise MoneyParseError("Failed to interpret value as non-negative decimal")
        quantized = positive.quantize(self.decimal_exponent)
        if positive != quantized:
            raise MoneyParseError(
                "Cannot interpret value as Money of currency {self.code} without loss "
                "of precision. Explicitly round the value or consider using "
                "MoneyFraction."
            )
        return quantized


C = TypeVar("C", bound=Currency)


class Money(Generic[C]):
    __slots__ = ("value", "currency", "__weakref__")

    def __init__(self, value: Decimal | int | str, currency: Currency | str) -> None:
        self.value: Final = PositiveDecimal.parse(value)
        self.currency: Final = currency

    def __repr__(self) -> str:
        return f"Money({self.value}, {self.currency})"

    @overload
    def __eq__(self, other: Literal[0]) -> bool:
        ...

    @overload
    def __eq__(self: Money[C], other: Money[C]) -> bool:
        ...

    @overload
    def __eq__(self, other: object) -> NotImplemented:
        ...

    def __eq__(self, other: object) -> bool:
        if isinstance(other, int) and other == 0:
            return self.value == other
        if isinstance(other, Money) and self.currency == other.currency:
            return self.value == other.value
        return NotImplemented

    @overload
    def __gt__(self: Money[C], other: Money[C]) -> bool:
        ...

    @overload
    def __gt__(self, other: object) -> NotImplemented:
        ...

    def __gt__(self, other: object) -> bool:
        if isinstance(other, Money) and self.currency == other.currency:
            return self.value > other.value
        return NotImplemented

    @overload
    def __add__(self: Money[C], other: Money[C]) -> Money[C]:
        ...

    @overload
    def __add__(self, other: object) -> NotImplemented:
        ...

    def __add__(self: Money[C], other: object) -> Money[C]:
        if isinstance(other, Money) and self.currency == other.currency:
            return Money(self.value + other.value, self.currency)
        return NotImplemented

    @overload
    def __truediv__(self, other: int) -> tuple[Self[C], ...]:
        ...

    @overload
    def __truediv__(self, other: object) -> NotImplemented:
        ...

    def __truediv__(self, other: object) -> tuple[Self[C], ...]:
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
        under = self.floored(self.value / other, self.currency)
        under_subunit = under.as_subunit()
        # TODO: Better name
        overflow = self.as_subunit() - under_subunit * other
        over = Money.from_subunit(under_subunit + 1, self.currency)

        return tuple(
            chain(
                (over for _ in range(overflow)),
                (under for _ in range(other - overflow)),
            )
        )

    @overload
    def __floordiv__(self, other: int) -> MoneyFraction[C]:
        ...

    @overload
    def __floordiv__(self, other: object) -> NotImplemented:
        ...

    def __floordiv__(self, other: object) -> MoneyFraction[C]:
        if not isinstance(other, int):
            return NotImplemented
        return MoneyFraction.from_money(self, other)

    def as_subunit(self) -> int:
        return int(self.currency.subunit * self.value)

    @classmethod
    def from_subunit(cls, value: int, currency: Currency) -> Self:
        return cls(Decimal(value) / currency.subunit, currency)

    @classmethod
    # This needs HKT to allow typing to work properly for subclasses of Money.
    def floored(cls, value: Decimal, currency: C) -> Money[C]:
        return cls(
            value.quantize(currency.decimal_exponent, rounding=ROUND_DOWN), currency
        )


class MoneyFraction(Generic[C]):
    __slots__ = ("value", "currency", "__weakref__")

    def __init__(self, value: Fraction, currency: Currency) -> None:
        self.value: Final = value
        self.currency: Final = currency

    @classmethod
    def from_money(cls, money: Money[C], denominator: int) -> MoneyFraction[C]:
        return MoneyFraction(Fraction(money.as_subunit(), denominator), money.currency)
