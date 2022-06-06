from __future__ import annotations

import abc
import math
from decimal import ROUND_DOWN
from decimal import Decimal
from fractions import Fraction
from functools import cached_property
from typing import Annotated
from typing import Final
from typing import Generic
from typing import Literal
from typing import TypeVar
from typing import overload

from abcattrs import Abstract
from abcattrs import abstractattrs

from ._primitives import PositiveDecimal
from .errors import MoneyParseError

CurrencySelf = TypeVar("CurrencySelf", bound="Currency")


# TODO: Make immutable
@abstractattrs
class Currency(abc.ABC):
    code: Annotated[str, Abstract]
    subunit: Annotated[int, Abstract]

    def __str__(self) -> str:
        return self.code

    def __call__(self: CurrencySelf, value: Decimal | int | str) -> Money[CurrencySelf]:
        ...

    @cached_property
    def decimal_exponent(self) -> Decimal:
        # Is there a smarter way to do this?
        return Decimal("0." + int(math.log10(self.subunit)) * "0")

    @cached_property
    def zero(self: CurrencySelf) -> Money[CurrencySelf]:
        return Money(0, self)

    def normalize_value(self, value: Decimal | int | str) -> PositiveDecimal:
        quantized = Decimal(value).quantize(self.decimal_exponent)

        try:
            positive = PositiveDecimal.parse(quantized)
        except (TypeError, ValueError) as e:
            raise MoneyParseError(
                "Failed to interpret value as non-negative decimal"
            ) from e

        if positive != quantized:
            raise MoneyParseError(
                "Cannot interpret value as Money of currency {self.code} without loss "
                "of precision. Explicitly round the value or consider using "
                "MoneyFraction."
            )

        return positive


C = TypeVar("C", bound=Currency)
MoneySelf = TypeVar("MoneySelf", bound="Money")


# TODO: Make immutable
class Money(Generic[C]):
    __slots__ = ("value", "currency", "__weakref__")

    def __init__(self, value: Decimal | int | str, currency: C) -> None:
        self.value: Final = PositiveDecimal.parse(value)
        self.currency: Final = currency

    def __repr__(self) -> str:
        return f"{type(self).__qualname__}({str(self.value)!r}, {self.currency})"

    @overload
    def __eq__(self, other: Literal[0]) -> bool:
        ...

    @overload
    def __eq__(self: Money[C], other: Money[C]) -> bool:
        ...

    @overload
    def __eq__(self, other: object) -> bool:
        ...

    def __eq__(self, other: object) -> bool:
        if isinstance(other, int) and other == 0:
            return self.value == other
        if isinstance(other, Money) and self.currency == other.currency:
            return self.value == other.value
        return NotImplemented

    def __gt__(self: Money[C], other: Money[C]) -> bool:
        if isinstance(other, Money) and self.currency == other.currency:
            return self.value > other.value
        return NotImplemented

    def __add__(self: Money[C], other: Money[C]) -> Money[C]:
        if isinstance(other, Money) and self.currency == other.currency:
            return Money(self.value + other.value, self.currency)
        return NotImplemented

    # TODO: Handle negative results with a Debt type.
    def __sub__(self: Money[C], other: Money[C]) -> Money[C] | Debt[C]:
        if isinstance(other, Money) and self.currency == other.currency:
            value = self.value - other.value
            return (
                Money(value, self.currency)
                if value >= 0
                else Debt(Money(-value, self.currency))
            )
        return NotImplemented

    # TODO: Support precision-lossy multiplication with floats?
    # TODO: Can the allowed multiplication types be reflected properly here?
    def __mul__(self, other: object) -> Money[C]:
        if isinstance(other, int):
            return Money(self.value * other, self.currency)
        return NotImplemented

    def __rmul__(self: Money[C], other: int) -> Money[C]:
        return self.__mul__(other)

    def __truediv__(self: Money[C], other: object) -> tuple[Money[C], ...]:
        """
        Divides the original value over the numerator and returns a tuple of new
        Money instances where the original value is spread as evenly as possible. The
        sum of the returned values will always equal the orignal value.

        >>> from immoney.currencies import SEK
        >>> Money(2, SEK) / 2
        (Money('1.00', SEK), Money('1.00', SEK))
        >>> Money(3, SEK) / 2
        (Money('1.50', SEK), Money('1.50', SEK))
        >>> Money("0.03", SEK) / 2
        (Money('0.02', SEK), Money('0.01', SEK))
        """
        if not isinstance(other, int):
            return NotImplemented
        under = self.floored(self.value / other, self.currency)
        under_subunit = under.as_subunit()
        remainder = self.as_subunit() - under_subunit * other
        over = Money[C].from_subunit(under_subunit + 1, self.currency)

        return (
            *(over for _ in range(remainder)),
            *(under for _ in range(other - remainder)),
        )

    def __floordiv__(self, other: object) -> MoneyFraction[C]:
        if not isinstance(other, int):
            return NotImplemented
        return MoneyFraction.from_money(self, other)

    def as_subunit(self) -> int:
        return int(self.currency.subunit * self.value)

    @classmethod
    def from_subunit(cls: type[MoneySelf], value: int, currency: Currency) -> MoneySelf:
        return cls(Decimal(value) / currency.subunit, currency)

    @classmethod
    # This needs HKT to allow typing to work properly for subclasses of Money.
    def floored(cls, value: Decimal, currency: C) -> Money[C]:
        return cls(
            value=value.quantize(currency.decimal_exponent, rounding=ROUND_DOWN),
            currency=currency,
        )


# TODO: Make immutable
class MoneyFraction(Generic[C]):
    __slots__ = ("value", "currency", "__weakref__")

    def __init__(self, value: Fraction, currency: Currency) -> None:
        self.value: Final = value
        self.currency: Final = currency

    @classmethod
    def from_money(cls, money: Money[C], denominator: int) -> MoneyFraction[C]:
        return MoneyFraction(Fraction(money.as_subunit(), denominator), money.currency)


# TODO: Make immutable
class Debt(Generic[C]):
    __slots__ = ("money", "__weakref__")

    def __init__(self, money: Money[C]) -> None:
        self.money: Final = money

    @overload
    def __eq__(self: Debt[C], other: Debt[C]) -> bool:
        ...

    @overload
    def __eq__(self, other: object) -> bool:
        ...

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Debt) and other.money.currency == self.money.currency:
            return self.money.value == other.money.value
        return NotImplemented
