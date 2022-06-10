from __future__ import annotations

import abc
import enum
import math
from decimal import ROUND_05UP
from decimal import ROUND_DOWN
from decimal import ROUND_HALF_DOWN
from decimal import ROUND_HALF_EVEN
from decimal import ROUND_HALF_UP
from decimal import ROUND_UP
from decimal import Decimal
from fractions import Fraction
from functools import cached_property
from typing import Any
from typing import ClassVar
from typing import Final
from typing import Generic
from typing import NoReturn
from typing import TypeVar
from typing import cast
from typing import overload

from abcattrs import Abstract
from abcattrs import abstractattrs

from ._primitives import PositiveDecimal
from .errors import FrozenInstanceError
from .errors import MoneyParseError

CurrencySelf = TypeVar("CurrencySelf", bound="Currency")


@abstractattrs
class Currency(abc.ABC):
    code: ClassVar[Abstract[str]]
    subunit: ClassVar[Abstract[int]]

    def __str__(self) -> str:
        return self.code

    def __repr__(self) -> str:
        return f"Currency(code={self.code}, subunit={self.subunit})"

    def __call__(self: CurrencySelf, value: Decimal | int | str) -> Money[CurrencySelf]:
        return Money(value, self)

    def __hash__(self) -> int:
        return hash((self.code, self.subunit))

    # Using NoReturn makes mypy give a type error for assignment to attributes (because
    # NoReturn is the bottom type).
    # TODO: Switch to typing_extensions.Never once available.
    def __setattr__(self, key: str, value: NoReturn) -> None:
        raise FrozenInstanceError(
            f"Currency instances are immutable, cannot write to attribute {key!r}"
        )

    @cached_property
    def decimal_exponent(self) -> Decimal:
        # Is there a smarter way to do this?
        return Decimal("0." + int(math.log10(self.subunit)) * "0")

    @cached_property
    def zero(self: CurrencySelf) -> Money[CurrencySelf]:
        return Money(0, self)

    def normalize_value(self, value: Decimal | int | str) -> PositiveDecimal:
        try:
            positive = PositiveDecimal.parse(value)
        except TypeError as e:
            raise MoneyParseError(
                "Failed to interpret value as non-negative decimal"
            ) from e

        quantized = cast(PositiveDecimal, positive.quantize(self.decimal_exponent))

        if positive != quantized:
            raise MoneyParseError(
                "Cannot interpret value as Money of currency {self.code} without loss "
                "of precision. Explicitly round the value or consider using "
                "SubunitFraction."
            )

        return quantized

    def from_subunit(
        self: CurrencySelf,
        value: Decimal | int | str,
    ) -> Money[CurrencySelf]:
        return Money.from_subunit(value, self)


C = TypeVar("C", bound=Currency)
MoneySelf = TypeVar("MoneySelf", bound="Money[Any]")


class Money(Generic[C]):
    __slots__ = ("value", "currency", "__weakref__")

    def __init__(self, value: Decimal | int | str, currency: C) -> None:
        if not isinstance(currency, Currency):
            raise TypeError(
                f"Argument currency of {type(self).__qualname__!r} must be a Currency, "
                f"got object of type {type(currency)!r}"
            )
        self.value: Final = currency.normalize_value(value)
        self.currency: Final = currency

    def __repr__(self) -> str:
        return f"{type(self).__qualname__}({str(self.value)!r}, {self.currency})"

    def __hash__(self) -> int:
        return hash((self.currency, self.value))

    # Using NoReturn makes mypy give a type error for assignment to attributes (because
    # NoReturn is the bottom type).
    # TODO: Switch to typing_extensions.Never once available.
    def __setattr__(self, key: str, value: NoReturn) -> None:
        if hasattr(self, "currency") and hasattr(self, "value"):
            raise FrozenInstanceError(
                f"Currency instances are immutable, cannot write to attribute {key!r}"
            )
        super().__setattr__(key, value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, int) and other == 0:
            return self.value == other
        if isinstance(other, Money):
            return self.currency == other.currency and self.value == other.value
        return NotImplemented

    def __gt__(self: Money[C], other: Money[C]) -> bool:
        if isinstance(other, Money) and self.currency == other.currency:
            return self.value > other.value
        return NotImplemented

    def __ge__(self: Money[C], other: Money[C]) -> bool:
        if isinstance(other, Money) and self.currency == other.currency:
            return self.value >= other.value
        return NotImplemented

    def __lt__(self: Money[C], other: Money[C]) -> bool:
        if isinstance(other, Money) and self.currency == other.currency:
            return self.value < other.value
        return NotImplemented

    def __le__(self: Money[C], other: Money[C]) -> bool:
        if isinstance(other, Money) and self.currency == other.currency:
            return self.value <= other.value
        return NotImplemented

    def __add__(self: Money[C], other: Money[C]) -> Money[C]:
        if isinstance(other, Money) and self.currency == other.currency:
            return Money(self.value + other.value, self.currency)
        return NotImplemented

    def __sub__(self: Money[C], other: Money[C]) -> Money[C] | Overdraft[C]:
        """
        >>> from immoney.currencies import SEK
        >>> SEK(2) - SEK(1)
        Money('1.00', SEK)
        >>> SEK(2) - SEK(2)
        Money('0.00', SEK)
        >>> SEK(2) - SEK(3)
        Overdraft('1.00', SEK)
        """
        if isinstance(other, Money) and self.currency == other.currency:
            value = self.value - other.value
            return (
                Money(value, self.currency)
                if value >= 0
                else Overdraft(Money(-value, self.currency))
            )
        return NotImplemented

    # TODO: Support precision-lossy multiplication with floats?
    # TODO: Can the allowed multiplication types be reflected properly here?
    # TODO: Support multiplication with negative value? Is it OK for SubunitFraction to
    #   support negative values? SubunitFraction.round() would need to return union of
    #   Money | Overdraft. Alternative would be to introduce SubunitFractionOverdraft,
    #   which like an amount of complexity that is hard to justify.
    @overload
    def __mul__(self: Money[C], other: int) -> Money[C]:
        ...

    @overload
    def __mul__(self: Money[C], other: Decimal) -> SubunitFraction[C]:
        ...

    def __mul__(self, other: object) -> Money[C] | SubunitFraction[C]:
        if isinstance(other, int) and other >= 0:
            return Money(self.value * other, self.currency)
        if isinstance(other, Decimal) and other >= 0:
            return SubunitFraction(Fraction(self.as_subunit() * other), self.currency)
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
        over = Money.from_subunit(under_subunit + 1, self.currency)

        return (
            *(over for _ in range(remainder)),
            *(under for _ in range(other - remainder)),
        )

    def __floordiv__(self, other: object) -> SubunitFraction[C]:
        if not isinstance(other, int):
            return NotImplemented
        return SubunitFraction.from_money(self, other)

    def as_subunit(self) -> int:
        return int(self.currency.subunit * self.value)

    @classmethod
    # This needs HKT to allow typing to work properly for subclasses of Money.
    def from_subunit(cls, value: int, currency: C) -> Money[C]:
        return cls(Decimal(value) / currency.subunit, currency)

    @classmethod
    # This needs HKT to allow typing to work properly for subclasses of Money.
    def floored(cls, value: Decimal, currency: C) -> Money[C]:
        return cls(
            value=value.quantize(currency.decimal_exponent, rounding=ROUND_DOWN),
            currency=currency,
        )


class Round(enum.Enum):
    """
    See Python documentation for decimal rounding.
    https://docs.python.org/3/library/decimal.html#rounding-modes
    """

    DOWN = ROUND_DOWN
    UP = ROUND_UP
    HALF_UP = ROUND_HALF_UP
    HALF_EVEN = ROUND_HALF_EVEN
    HALF_DOWN = ROUND_HALF_DOWN
    ZERO_FIVE_UP = ROUND_05UP


# TODO: Make immutable
class SubunitFraction(Generic[C]):
    __slots__ = ("value", "currency", "__weakref__")

    # FIXME: Check values at instantiation.
    def __init__(self, value: Fraction | Decimal, currency: C) -> None:
        self.value: Final = Fraction(value)
        self.currency: Final = currency

    def __repr__(self) -> str:
        return f"{type(self).__qualname__}" f"({str(self.value)!r}, {self.currency})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, SubunitFraction) and self.currency == other.currency:
            return self.value == other.value
        if isinstance(other, Money) and self.currency == other.currency:
            return self.value == other.as_subunit()
        return NotImplemented

    @classmethod
    def from_money(cls, money: Money[C], denominator: int) -> SubunitFraction[C]:
        return SubunitFraction(
            Fraction(money.as_subunit(), denominator), money.currency
        )

    def round(self, rounding: Round) -> Money[C]:
        main_unit = Decimal(float(self.value / self.currency.subunit))
        quantized = main_unit.quantize(
            exp=self.currency.decimal_exponent,
            rounding=rounding.value,
        )
        return Money(quantized, self.currency)


# TODO: Make immutable
class Overdraft(Generic[C]):
    __slots__ = ("money", "__weakref__")

    def __init__(self, money: Money[C]) -> None:
        self.money: Final = money

    def __repr__(self) -> str:
        return (
            f"{type(self).__qualname__}"
            f"({str(self.money.value)!r}, {self.money.currency})"
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Overdraft) and other.money.currency == self.money.currency:
            return self.money.value == other.money.value
        return NotImplemented

    @overload
    def __add__(self: Overdraft[C], other: Money[C]) -> Money[C] | Overdraft[C]:
        ...

    @overload
    def __add__(self: Overdraft[C], other: Overdraft[C]) -> Overdraft[C]:
        ...

    def __add__(self: Overdraft[C], other: object) -> Money[C] | Overdraft[C]:
        if isinstance(other, Money):
            return other - self.money
        if isinstance(other, Overdraft):
            return Overdraft(self.money + other.money)
        return NotImplemented
