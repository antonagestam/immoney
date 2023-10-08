from __future__ import annotations

import abc
import decimal
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
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar
from typing import Final
from typing import Generic
from typing import NewType
from typing import TypeAlias
from typing import TypeVar
from typing import final
from typing import overload

from abcattrs import Abstract
from abcattrs import abstractattrs
from typing_extensions import Self

from ._cache import InstanceCache
from ._frozen import Frozen
from .errors import DivisionByZero
from .errors import InvalidOverdraftValue
from .errors import InvalidSubunit
from .errors import ParseError

if TYPE_CHECKING:
    from pydantic_core.core_schema import CoreSchema

    from .registry import CurrencyRegistry

ParsableMoneyValue: TypeAlias = int | str | Decimal
PositiveDecimal = NewType("PositiveDecimal", Decimal)

valid_subunit: Final = frozenset({10**i for i in range(20)})


@abstractattrs
class Currency(Frozen, abc.ABC):
    code: ClassVar[Abstract[str]]
    subunit: ClassVar[Abstract[int]]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        # Skip validation on intermediary base classes.
        if abc.ABC in cls.__bases__:
            return
        if cls.subunit not in valid_subunit:
            raise InvalidSubunit(
                "Currency subunits other than powers of 10 are not supported"
            )

    def __str__(self) -> str:
        return self.code

    def __repr__(self) -> str:
        return f"Currency(code={self.code}, subunit={self.subunit})"

    def __call__(self, value: ParsableMoneyValue) -> Money[Self]:
        return Money(value, self)

    def __hash__(self) -> int:
        return hash((type(self), self.code, self.subunit))

    @cached_property
    def decimal_exponent(self) -> Decimal:
        # Is there a smarter way to do this?
        return Decimal("0." + int(math.log10(self.subunit)) * "0")

    @cached_property
    def zero(self) -> Money[Self]:
        return Money(0, self)

    def normalize_value(self, value: Decimal | int | str) -> PositiveDecimal:
        if not isinstance(value, Decimal):
            try:
                value = Decimal(value)
            except decimal.InvalidOperation:
                raise ParseError("Failed parsing Decimal")

        if value.is_nan():
            raise ParseError("Cannot parse from NaN")

        if not value.is_finite():
            raise ParseError("Cannot parse from non-finite")

        if value < 0:
            raise ParseError("Cannot parse from negative value")

        quantized = value.quantize(self.decimal_exponent)

        if value != quantized:
            raise ParseError(
                f"Cannot interpret value as Money of currency {self.code} without loss "
                f"of precision. Explicitly round the value or consider using "
                f"SubunitFraction."
            )

        return PositiveDecimal(quantized)

    def from_subunit(self, value: int) -> Money[Self]:
        return Money.from_subunit(value, self)

    def overdraft_from_subunit(self, value: int) -> Overdraft[Self]:
        return Overdraft.from_subunit(value, self)

    @cached_property
    def one_subunit(self) -> Money[Self]:
        return self.from_subunit(1)

    def fraction(
        self,
        subunit_value: Fraction | Decimal | int,
    ) -> SubunitFraction[Self]:
        return SubunitFraction(subunit_value, self)

    def overdraft(self: Self, value: ParsableMoneyValue) -> Overdraft[Self]:
        return Overdraft(value, self)

    @classmethod
    def get_default_registry(cls) -> CurrencyRegistry[Currency]:
        from .currencies import registry

        return registry

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        *args: object,
        **kwargs: object,
    ) -> CoreSchema:
        from ._pydantic import build_currency_schema

        return build_currency_schema(cls)


def _validate_currency_arg(
    cls: type,
    value: object,
    arg_name: str = "currency",
) -> None:
    if not isinstance(value, Currency):
        raise TypeError(
            f"Argument {arg_name!r} of {cls.__qualname__!r} must be a Currency, "
            f"got object of type {type(value)!r}"
        )


def _dispatch_type(value: Decimal, currency: C_inv) -> Money[C_inv] | Overdraft[C_inv]:
    return Money(value, currency) if value >= 0 else Overdraft(-value, currency)


C_co = TypeVar("C_co", bound=Currency, covariant=True)


class _ValueCurrencyPair(Frozen, Generic[C_co], metaclass=InstanceCache):
    __slots__ = ("value", "currency")

    def __init__(self, value: ParsableMoneyValue, currency: C_co, /) -> None:
        # Type ignore is safe because metaclass delegates normalization to _normalize().
        self.value: Final[Decimal] = value  # type: ignore[assignment]
        self.currency: Final = currency

    def __repr__(self) -> str:
        return f"{type(self).__qualname__}({str(self.value)!r}, {self.currency})"

    @property
    def subunits(self) -> int:
        return int(self.currency.subunit * self.value)


C_inv = TypeVar("C_inv", bound=Currency, covariant=False, contravariant=False)


@final
class Money(_ValueCurrencyPair[C_co], Generic[C_co]):
    @classmethod
    def _normalize(
        cls,
        value: ParsableMoneyValue,
        currency: C_inv,
        /,
    ) -> tuple[PositiveDecimal, C_inv]:
        _validate_currency_arg(cls, currency)
        return currency.normalize_value(value), currency

    def __hash__(self) -> int:
        return hash((type(self), self.currency, self.value))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, int) and other == 0:
            return self.value == other
        if isinstance(other, Money):
            return self.currency == other.currency and self.value == other.value
        return NotImplemented

    def __gt__(self: Money[C_co], other: Money[C_co]) -> bool:
        if isinstance(other, Money) and self.currency == other.currency:
            return self.value > other.value
        return NotImplemented

    def __ge__(self: Money[C_co], other: Money[C_co]) -> bool:
        if isinstance(other, Money) and self.currency == other.currency:
            return self.value >= other.value
        return NotImplemented

    def __lt__(self: Money[C_co], other: Money[C_co]) -> bool:
        if isinstance(other, Money) and self.currency == other.currency:
            return self.value < other.value
        return NotImplemented

    def __le__(self: Money[C_co], other: Money[C_co]) -> bool:
        if isinstance(other, Money) and self.currency == other.currency:
            return self.value <= other.value
        return NotImplemented

    def __iadd__(self: Money[C_co], other: Money[C_co]) -> Money[C_co]:
        if isinstance(other, Money) and self.currency == other.currency:
            return Money(self.value + other.value, self.currency)
        return NotImplemented

    def __add__(self: Money[C_co], other: Money[C_co]) -> Money[C_co]:
        if isinstance(other, Money) and self.currency == other.currency:
            return Money(self.value + other.value, self.currency)
        return NotImplemented

    def __sub__(self: Money[C_co], other: Money[C_co]) -> Money[C_co] | Overdraft[C_co]:
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
            return _dispatch_type(value, self.currency)
        return NotImplemented

    def __pos__(self) -> Self:
        return self

    def __neg__(self: Money[C_co]) -> Overdraft[C_co] | Money[C_co]:
        return self if self.value == 0 else Overdraft(self.value, self.currency)

    # TODO: Support precision-lossy multiplication with floats?
    @overload
    def __mul__(self: Money[C_co], other: int) -> Money[C_co] | Overdraft[C_co]:
        ...

    @overload
    def __mul__(self: Money[C_co], other: Decimal) -> SubunitFraction[C_co]:
        ...

    def __mul__(
        self,
        other: object,
    ) -> Money[C_co] | SubunitFraction[C_co] | Overdraft[C_co]:
        if isinstance(other, int):
            return _dispatch_type(self.value * other, self.currency)
        if isinstance(other, Decimal):
            return SubunitFraction(
                Fraction(self.subunits) * Fraction(other),
                self.currency,
            )
        return NotImplemented

    @overload
    def __rmul__(self: Money[C_co], other: int) -> Money[C_co] | Overdraft[C_co]:
        ...

    @overload
    def __rmul__(self: Money[C_co], other: Decimal) -> SubunitFraction[C_co]:
        ...

    def __rmul__(
        self: Money[C_co],
        other: int | Decimal,
    ) -> Money[C_co] | SubunitFraction[C_co] | Overdraft[C_co]:
        return self.__mul__(other)

    def __truediv__(self: Money[C_co], other: object) -> tuple[Money[C_co], ...]:
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

        try:
            under = self.floored(self.value / other, self.currency)
        except decimal.DivisionByZero as e:
            raise DivisionByZero from e

        under_subunit = under.subunits
        remainder = self.subunits - under_subunit * other
        over = Money.from_subunit(under_subunit + 1, self.currency)

        return (
            *(over for _ in range(remainder)),
            *(under for _ in range(other - remainder)),
        )

    @overload
    def __floordiv__(self, other: int) -> SubunitFraction[C_co]:
        ...

    @overload
    def __floordiv__(self, other: Fraction) -> SubunitFraction[C_co]:
        ...

    def __floordiv__(self, other: object) -> SubunitFraction[C_co]:
        if not isinstance(other, (int, Fraction)):
            return NotImplemented
        if other == 0:
            raise DivisionByZero
        return SubunitFraction.from_money(self, other)

    def __abs__(self) -> Self:
        return self

    @classmethod
    # This needs HKT to allow typing to work properly for subclasses of Money.
    def from_subunit(cls, value: int, currency: C_inv) -> Money[C_inv]:
        return cls(  # type: ignore[return-value]
            Decimal(value) / currency.subunit,
            currency,  # type: ignore[arg-type]
        )

    @classmethod
    # This needs HKT to allow typing to work properly for subclasses of Money.
    def floored(cls, value: Decimal, currency: C_inv) -> Money[C_inv]:
        return cls(  # type: ignore[return-value]
            value.quantize(currency.decimal_exponent, rounding=ROUND_DOWN),
            currency,  # type: ignore[arg-type]
        )

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: type,
        *args: object,
        **kwargs: object,
    ) -> CoreSchema:
        from ._pydantic import MoneyAdapter
        from ._pydantic import build_generic_currency_schema

        return build_generic_currency_schema(
            cls=cls,
            source_type=source_type,
            adapter=MoneyAdapter,
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


@final
class SubunitFraction(Frozen, Generic[C_co], metaclass=InstanceCache):
    __slots__ = ("value", "currency")

    def __init__(self, value: Fraction | Decimal | int, currency: C_co, /) -> None:
        self.value: Final = Fraction(value)
        self.currency: Final = currency

    @classmethod
    def _normalize(
        cls,
        value: Fraction | Decimal,
        currency: C_inv,
    ) -> tuple[Fraction, C_inv]:
        if not isinstance(currency, Currency):
            raise TypeError(
                f"Argument 'currency' of {cls.__qualname__!r} must be a Currency, "
                f"got object of type {type(currency)!r}"
            )
        return Fraction(value), currency

    def __repr__(self) -> str:
        return f"{type(self).__qualname__}" f"({str(self.value)!r}, {self.currency})"

    def __hash__(self) -> int:
        return hash((type(self), self.currency, self.value))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, int) and other == 0:
            return self.value == other
        if isinstance(other, SubunitFraction) and self.currency == other.currency:
            return self.value == other.value
        if isinstance(other, Money) and self.currency == other.currency:
            return self.value == other.subunits
        return NotImplemented

    @classmethod
    def from_money(
        cls,
        money: Money[C_co],
        denominator: int | Fraction = 1,
    ) -> SubunitFraction[C_co]:
        return SubunitFraction(Fraction(money.subunits, denominator), money.currency)

    def _round_value(self, rounding: Round) -> Decimal:
        main_unit = Decimal(float(self.value / self.currency.subunit))
        return main_unit.quantize(
            exp=self.currency.decimal_exponent,
            rounding=rounding.value,
        )

    def round_either(self, rounding: Round) -> Money[C_co] | Overdraft[C_co]:
        return _dispatch_type(self._round_value(rounding), self.currency)

    def round_money(self, rounding: Round) -> Money[C_co]:
        return Money(self._round_value(rounding), self.currency)

    def round_overdraft(self, rounding: Round) -> Overdraft[C_co]:
        return Overdraft(-self._round_value(rounding), self.currency)

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: type,
        *args: object,
        **kwargs: object,
    ) -> CoreSchema:
        from ._pydantic import SubunitFractionAdapter
        from ._pydantic import build_generic_currency_schema

        return build_generic_currency_schema(
            cls=cls,
            source_type=source_type,
            adapter=SubunitFractionAdapter,
        )


@final
class Overdraft(_ValueCurrencyPair[C_co], Generic[C_co]):
    @classmethod
    def _normalize(
        cls,
        value: ParsableMoneyValue,
        currency: C_inv,
        /,
    ) -> tuple[PositiveDecimal, C_inv]:
        _validate_currency_arg(cls, currency)
        normalized_value = currency.normalize_value(value)
        if normalized_value == 0:
            raise InvalidOverdraftValue(
                f"{cls.__qualname__} cannot be instantiated with a value of zero, "
                f"the {Money.__qualname__} class should be used instead."
            )
        return currency.normalize_value(value), currency

    def __hash__(self) -> int:
        return hash((type(self), self.currency, self.value))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Overdraft):
            return self.currency == other.currency and self.value == other.value
        return NotImplemented

    @overload
    def __add__(
        self: Overdraft[C_co],
        other: Money[C_co],
    ) -> Money[C_co] | Overdraft[C_co]:
        ...

    @overload
    def __add__(self: Overdraft[C_co], other: Overdraft[C_co]) -> Overdraft[C_co]:
        ...

    def __add__(self: Overdraft[C_co], other: object) -> Money[C_co] | Overdraft[C_co]:
        if isinstance(other, Overdraft) and self.currency == other.currency:
            return Overdraft(self.value + other.value, self.currency)
        if isinstance(other, Money) and self.currency == other.currency:
            return _dispatch_type(other.value - self.value, self.currency)
        return NotImplemented

    def __radd__(
        self: Overdraft[C_co],
        other: Money[C_co],
    ) -> Money[C_co] | Overdraft[C_co]:
        return self.__add__(other)

    @overload
    def __sub__(self: Overdraft[C_co], other: Money[C_co]) -> Overdraft[C_co]:
        ...

    @overload
    def __sub__(
        self: Overdraft[C_co],
        other: Overdraft[C_co],
    ) -> Money[C_co] | Overdraft[C_co]:
        ...

    def __sub__(
        self: Overdraft[C_co],
        other: Money[C_co] | Overdraft[C_co],
    ) -> Money[C_co] | Overdraft[C_co]:
        if not isinstance(other, Money | Overdraft) or self.currency != other.currency:
            return NotImplemented

        value = (
            self.value - other.value
            if isinstance(other, Overdraft)
            else -(self.value + other.value)
        )

        return _dispatch_type(value, self.currency)

    def __rsub__(self: Overdraft[C_co], other: Money[C_co]) -> Money[C_co]:
        if isinstance(other, Money) and self.currency == other.currency:
            # In the interpretation that an overdraft is a negative value, this is
            # equivalent to subtracting a negative value, which can be equivalently
            # rewritten as an addition (x - (-y) == x + y).
            return Money(self.value + other.value, self.currency)
        return NotImplemented

    def __abs__(self: Overdraft[C_co]) -> Money[C_co]:
        return Money(self.value, self.currency)

    def __neg__(self: Overdraft[C_co]) -> Money[C_co]:
        return Money(self.value, self.currency)

    def __pos__(self: Overdraft[C_co]) -> Overdraft[C_co]:
        return self

    @classmethod
    # This needs HKT to allow typing to work properly for subclasses of Overdraft, that
    # would also allow moving the implementation to the shared super-class.
    def from_subunit(cls, value: int, currency: C_inv) -> Overdraft[C_inv]:
        return cls(  # type: ignore[return-value]
            Decimal(value) / currency.subunit,
            currency,  # type: ignore[arg-type]
        )

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: type,
        *args: object,
        **kwargs: object,
    ) -> CoreSchema:
        from ._pydantic import OverdraftAdapter
        from ._pydantic import build_generic_currency_schema

        return build_generic_currency_schema(
            cls=cls,
            source_type=source_type,
            adapter=OverdraftAdapter,
        )
