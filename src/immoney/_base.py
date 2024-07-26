from __future__ import annotations

import abc
import enum
import math
from decimal import Decimal
from fractions import Fraction
from functools import cached_property
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar
from typing import Final
from typing import Generic
from typing import TypeAlias
from typing import TypeVar
from typing import final
from typing import overload

from abcattrs import Abstract
from abcattrs import abstractattrs
from typing_extensions import Self
from typing_extensions import assert_never

from ._cache import InstanceCache
from ._frozen import Frozen
from ._parsers import Nat
from ._parsers import approximate_decimal_subunits
from ._parsers import parse_nat
from .errors import DivisionByZero
from .errors import InvalidOverdraftValue
from .errors import InvalidSubunit
from .errors import ParseError

if TYPE_CHECKING:
    from pydantic_core.core_schema import CoreSchema

    from .registry import CurrencyRegistry


ParsableMoneyValue: TypeAlias = int | str | Decimal

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
    def subunit_width(self) -> int:
        return math.ceil(math.log10(self.subunit))

    @cached_property
    def decimal_exponent(self) -> Decimal:
        return Decimal("0." + self.subunit_width * "0")

    @cached_property
    def zero(self) -> Money[Self]:
        return Money(0, self)

    def normalize_to_subunits(self, main_unit: object) -> Nat:
        """
        Takes a raw money value as Decimal, int, or str, and parses it into a valid
        subunit value.
        """
        if isinstance(main_unit, int):
            return parse_nat(main_unit * self.subunit)

        if not isinstance(main_unit, str | Decimal):
            raise NotImplementedError(
                f"Cannot parse money from value of type {type(main_unit)!r}."
            )

        approximated = approximate_decimal_subunits(main_unit, self.subunit)
        exact = int(approximated)
        if approximated != exact:
            raise ParseError(
                f"Cannot interpret value as Money of currency {self.code!r} "
                f"without loss of precision. Explicitly round the value or "
                f"consider using SubunitFraction."
            )

        return parse_nat(exact)

    def from_subunit(self, value: int) -> Money[Self]:
        return Money.from_subunit(value, self)

    def overdraft_from_subunit(self, value: int) -> Overdraft[Self]:
        return Overdraft.from_subunit(value, self)

    @cached_property
    def one_subunit(self) -> Money[Self]:
        return self.from_subunit(1)

    @overload
    def fraction(
        self,
        a: int,
        b: int,
        /,
    ) -> SubunitFraction[Self]: ...

    @overload
    def fraction(
        self,
        subunit_value: Fraction | Decimal | int,
    ) -> SubunitFraction[Self]: ...

    def fraction(
        self,
        subunit_value: Fraction | Decimal | int,
        denominator: int | None = None,
    ) -> SubunitFraction[Self]:
        if denominator is not None:
            if not isinstance(subunit_value, int):
                raise TypeError("Incorrect signature for Currency.fraction()")
            return SubunitFraction(Fraction(subunit_value, denominator), self)
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


def _parse_currency_from_arg(
    cls: type,
    value: object,
    arg_name: str = "currency",
) -> Currency:
    if not isinstance(value, Currency):
        raise TypeError(
            f"Argument {arg_name!r} of {cls.__qualname__!r} must be a Currency, "
            f"got object of type {type(value)!r}"
        )
    return value


def _dispatch_type(subunits: int, currency: C_inv) -> Money[C_inv] | Overdraft[C_inv]:
    return (
        Money.from_subunit(subunits, currency)
        if subunits >= 0
        else Overdraft.from_subunit(-subunits, currency)
    )


C_co = TypeVar("C_co", bound=Currency, covariant=True)


class _ValueCurrencyPair(Frozen, Generic[C_co], metaclass=InstanceCache):
    __slots__ = ("subunits", "currency")

    @overload
    def __init__(self, *, subunits: int, currency: C_co) -> None: ...

    @overload
    def __init__(self, value: ParsableMoneyValue, currency: C_co, /) -> None: ...

    def __init__(  # type: ignore[misc]
        self,
        value: ParsableMoneyValue,
        currency: C_co,
    ) -> None:
        # Type ignore is safe because metaclass delegates normalization to _normalize().
        self.subunits: Final[Nat] = value  # type: ignore[assignment]
        self.currency: Final = currency

    @classmethod
    def _normalize(
        cls,
        *args: object,
        **kwargs: object,
    ) -> tuple[Nat, Currency]:
        match args, kwargs:
            case ((value, currency_arg), {}):
                currency = _parse_currency_from_arg(cls, currency_arg)
                return currency.normalize_to_subunits(value), currency
            case ((), {"subunits": int(subunits), "currency": currency_arg}):
                currency = _parse_currency_from_arg(cls, currency_arg)
                return parse_nat(subunits), currency
            case _:
                raise TypeError(f"Invalid call signature for {cls.__qualname__}")

    def __repr__(self) -> str:
        main_unit, subunits = self.str_parts()
        return f"{type(self).__qualname__}('{main_unit}.{subunits}', {self.currency})"

    @property
    def decimal(self) -> Decimal:
        value = Decimal(self.subunits) / self.currency.subunit
        return value.quantize(self.currency.decimal_exponent)

    def str_parts(self) -> tuple[str, str]:
        string_value = str(self.subunits)
        subunit_width = self.currency.subunit_width
        length = len(string_value)
        return (
            ("0", "0" * (subunit_width - length) + string_value)
            if length <= subunit_width
            else (string_value[:-subunit_width], string_value[-subunit_width:])
        )


C_inv = TypeVar("C_inv", bound=Currency, covariant=False, contravariant=False)


@final
class Money(_ValueCurrencyPair[C_co], Generic[C_co]):
    def __str__(self) -> str:
        main_units, subunits = self.str_parts()
        return f"{main_units}.{subunits}\xa0{self.currency.code}"

    def __hash__(self) -> int:
        return hash((type(self), self.currency, self.subunits))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, int) and other == 0:
            return self.subunits == other
        if isinstance(other, Money):
            return self.currency == other.currency and self.subunits == other.subunits
        return NotImplemented

    def __gt__(self: Money[C_co], other: Money[C_co]) -> bool:
        if isinstance(other, Money) and self.currency == other.currency:
            return self.subunits > other.subunits
        return NotImplemented

    def __ge__(self: Money[C_co], other: Money[C_co]) -> bool:
        if isinstance(other, Money) and self.currency == other.currency:
            return self.subunits >= other.subunits
        return NotImplemented

    def __lt__(self: Money[C_co], other: Money[C_co]) -> bool:
        if isinstance(other, Money) and self.currency == other.currency:
            return self.subunits < other.subunits
        return NotImplemented

    def __le__(self: Money[C_co], other: Money[C_co]) -> bool:
        if isinstance(other, Money) and self.currency == other.currency:
            return self.subunits <= other.subunits
        return NotImplemented

    def __iadd__(self: Money[C_co], other: Money[C_co]) -> Money[C_co]:
        return self.__add__(other)

    def __add__(self: Money[C_co], other: Money[C_co]) -> Money[C_co]:
        if isinstance(other, Money) and self.currency == other.currency:
            return self.currency.from_subunit(self.subunits + other.subunits)
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
            return _dispatch_type(self.subunits - other.subunits, self.currency)
        return NotImplemented

    def __pos__(self) -> Self:
        return self

    def __neg__(self: Money[C_co]) -> Overdraft[C_co] | Money[C_co]:
        return (
            self
            if self.subunits == 0
            else self.currency.overdraft_from_subunit(self.subunits)
        )

    @overload
    def __mul__(self, other: int) -> Self | Overdraft[C_co]: ...

    @overload
    def __mul__(self, other: Decimal) -> SubunitFraction[C_co]: ...

    @overload
    def __mul__(self, other: Fraction) -> SubunitFraction[C_co]: ...

    def __mul__(
        self,
        other: object,
    ) -> SubunitFraction[C_co] | Overdraft[C_co] | Self:
        if isinstance(other, int):
            return _dispatch_type(self.subunits * other, self.currency)
        if isinstance(other, Fraction):
            return SubunitFraction(self.subunits * other, self.currency)
        if isinstance(other, Decimal):
            return SubunitFraction(
                Fraction(self.subunits) * Fraction(other),
                self.currency,
            )
        return NotImplemented

    @overload
    def __rmul__(self, other: int) -> Self | Overdraft[C_co]: ...

    @overload
    def __rmul__(self, other: Decimal) -> SubunitFraction[C_co]: ...

    @overload
    def __rmul__(self, other: Fraction) -> SubunitFraction[C_co]: ...

    def __rmul__(
        self,
        other: int | Decimal | Fraction,
    ) -> SubunitFraction[C_co] | Overdraft[C_co] | Self:
        return self.__mul__(other)

    def __floordiv__(self: Money[C_co], other: object) -> tuple[Money[C_co], ...]:
        """
        Divides the original value over the numerator and returns a tuple of new
        Money instances where the original value is spread as evenly as possible. The
        sum of the returned values will always equal the orignal value.

        >>> from immoney.currencies import SEK
        >>> Money(2, SEK) // 2
        (Money('1.00', SEK), Money('1.00', SEK))
        >>> Money(3, SEK) // 2
        (Money('1.50', SEK), Money('1.50', SEK))
        >>> Money("0.03", SEK) // 2
        (Money('0.02', SEK), Money('0.01', SEK))
        """
        if not isinstance(other, int):
            return NotImplemented

        try:
            under = self.currency.from_subunit(self.subunits // other)
        except ZeroDivisionError as e:
            raise DivisionByZero from e

        under_subunit = under.subunits
        remainder = self.subunits - under_subunit * other
        over = self.currency.from_subunit(under_subunit + 1)

        return (
            *(over for _ in range(remainder)),
            *(under for _ in range(other - remainder)),
        )

    @overload
    def __truediv__(self, other: int) -> SubunitFraction[C_co]: ...

    @overload
    def __truediv__(self, other: Fraction) -> SubunitFraction[C_co]: ...

    def __truediv__(self, other: object) -> SubunitFraction[C_co]:
        if not isinstance(other, int | Fraction):
            return NotImplemented
        if other == 0:
            raise DivisionByZero
        return SubunitFraction.from_money(self, other)

    @overload
    def __rtruediv__(self, other: int) -> SubunitFraction[C_co]: ...

    @overload
    def __rtruediv__(self, other: Fraction) -> SubunitFraction[C_co]: ...

    def __rtruediv__(self, other: object) -> SubunitFraction[C_co]:
        if not isinstance(other, int | Fraction):
            return NotImplemented
        if self.subunits == 0:
            raise DivisionByZero
        if other == 0:
            return SubunitFraction(0, self.currency)
        return 1 / SubunitFraction.from_money(self, other)

    def __abs__(self) -> Self:
        return self

    @classmethod
    # This needs HKT to allow typing to work properly for subclasses of Money.
    def from_subunit(cls, value: int, currency: C_inv) -> Money[C_inv]:
        return cls(
            subunits=value,
            currency=currency,
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

    DOWN = enum.auto()
    UP = enum.auto()
    HALF_UP = enum.auto()
    HALF_EVEN = enum.auto()
    HALF_DOWN = enum.auto()


HALF: Final = Fraction(1, 2)


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
        currency: Currency,
    ) -> tuple[Fraction, Currency]:
        return Fraction(value), _parse_currency_from_arg(cls, currency)

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
        if isinstance(other, Overdraft) and self.currency == other.currency:
            return self.value == -other.subunits
        return NotImplemented

    def __gt__(self, other: Self | Money[C_co] | Overdraft[C_co]) -> bool:
        if isinstance(other, SubunitFraction) and self.currency == other.currency:
            return self.value > other.value
        if isinstance(other, Money) and self.currency == other.currency:
            return self.value > other.subunits
        if isinstance(other, Overdraft) and self.currency == other.currency:
            return self.value > -other.subunits
        return NotImplemented

    def __ge__(self, other: Self | Money[C_co] | Overdraft[C_co]) -> bool:
        if isinstance(other, SubunitFraction) and self.currency == other.currency:
            return self.value >= other.value
        if isinstance(other, Money) and self.currency == other.currency:
            return self.value >= other.subunits
        if isinstance(other, Overdraft) and self.currency == other.currency:
            return self.value >= -other.subunits
        return NotImplemented

    def __lt__(self, other: Self | Money[C_co] | Overdraft[C_co]) -> bool:
        if isinstance(other, SubunitFraction) and self.currency == other.currency:
            return self.value < other.value
        if isinstance(other, Money) and self.currency == other.currency:
            return self.value < other.subunits
        if isinstance(other, Overdraft) and self.currency == other.currency:
            return self.value < -other.subunits
        return NotImplemented

    def __le__(self, other: Self | Money[C_co] | Overdraft[C_co]) -> bool:
        if isinstance(other, SubunitFraction) and self.currency == other.currency:
            return self.value <= other.value
        if isinstance(other, Money) and self.currency == other.currency:
            return self.value <= other.subunits
        if isinstance(other, Overdraft) and self.currency == other.currency:
            return self.value <= -other.subunits
        return NotImplemented

    def __neg__(self) -> SubunitFraction[C_co]:
        return SubunitFraction(-self.value, self.currency)

    def __add__(
        self,
        other: SubunitFraction[C_co] | Money[C_co] | Overdraft[C_co],
    ) -> Self:
        if isinstance(other, SubunitFraction) and self.currency == other.currency:
            return SubunitFraction(self.value + other.value, self.currency)
        if isinstance(other, Money) and self.currency == other.currency:
            return SubunitFraction(self.value + other.subunits, self.currency)
        if isinstance(other, Overdraft) and self.currency == other.currency:
            return SubunitFraction(self.value - other.subunits, self.currency)
        return NotImplemented

    def __radd__(self, other: Money[C_co] | Overdraft[C_co]) -> Self:
        return self.__add__(other)

    def __sub__(
        self,
        other: SubunitFraction[C_co] | Money[C_co] | Overdraft[C_co],
    ) -> Self:
        if isinstance(other, SubunitFraction) and self.currency == other.currency:
            return SubunitFraction(self.value - other.value, self.currency)
        if isinstance(other, Money) and self.currency == other.currency:
            return SubunitFraction(self.value - other.subunits, self.currency)
        if isinstance(other, Overdraft) and self.currency == other.currency:
            return SubunitFraction(self.value + other.subunits, self.currency)
        return NotImplemented

    def __rsub__(self, other: Money[C_co] | Overdraft[C_co]) -> Self:
        return self.__sub__(-other)

    @overload
    def __mul__(self, other: int) -> Self: ...

    @overload
    def __mul__(self, other: Fraction) -> Self: ...

    def __mul__(self, other: object) -> Self:
        if isinstance(other, int | Fraction):
            return SubunitFraction(self.value * other, self.currency)
        return NotImplemented

    def __rmul__(self, other: int | Fraction) -> Self:
        return self.__mul__(other)

    @overload
    def __truediv__(self, other: int) -> Self: ...

    @overload
    def __truediv__(self, other: Fraction) -> Self: ...

    def __truediv__(self, other: object) -> Self:
        if isinstance(other, int | Fraction):
            return SubunitFraction(self.value / other, self.currency)
        return NotImplemented

    @overload
    def __rtruediv__(self, other: int) -> Self: ...

    @overload
    def __rtruediv__(self, other: Fraction) -> Self: ...

    def __rtruediv__(self, other: object) -> Self:
        if isinstance(other, int | Fraction):
            return SubunitFraction(other / self.value, self.currency)
        return NotImplemented

    @classmethod
    def from_money(
        cls,
        money: Money[C_co],
        denominator: int | Fraction = 1,
    ) -> SubunitFraction[C_co]:
        return SubunitFraction(
            Fraction(money.subunits, denominator),
            money.currency,
        )

    @classmethod
    def from_overdraft(
        cls,
        overdraft: Overdraft[C_co],
        denominator: int | Fraction = 1,
    ) -> SubunitFraction[C_co]:
        return SubunitFraction(
            Fraction(-overdraft.subunits, denominator),
            overdraft.currency,
        )

    def _round_subunit(self, rounding: Round) -> int:
        remainder = self.value % 1

        match rounding:
            case Round.DOWN:
                return math.floor(self.value)
            case Round.UP:
                return math.ceil(self.value)
            case Round.HALF_UP:
                if remainder >= HALF:
                    return math.ceil(self.value)
                else:
                    return math.floor(self.value)
            case Round.HALF_EVEN:
                return round(self.value)
            case Round.HALF_DOWN:
                if remainder > HALF:
                    return math.ceil(self.value)
                else:
                    return math.floor(self.value)
            case no_match:
                assert_never(no_match)

    def round_either(self, rounding: Round) -> Money[C_co] | Overdraft[C_co]:
        return _dispatch_type(self._round_subunit(rounding), self.currency)

    def round_money(self, rounding: Round) -> Money[C_co]:
        return self.currency.from_subunit(self._round_subunit(rounding))

    def round_overdraft(self, rounding: Round) -> Overdraft[C_co]:
        return self.currency.overdraft_from_subunit(-self._round_subunit(rounding))

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
        *args: object,
        **kwargs: object,
    ) -> tuple[Nat, Currency]:
        subunits, currency = super()._normalize(*args, **kwargs)
        if subunits == 0:
            raise InvalidOverdraftValue(
                f"{cls.__qualname__} cannot be instantiated with a value of zero, "
                f"the {Money.__qualname__} class should be used instead."
            )
        return subunits, currency

    def __str__(self) -> str:
        main_units, subunits = self.str_parts()
        return f"-{main_units}.{subunits}\xa0{self.currency.code}"

    def __hash__(self) -> int:
        return hash((type(self), self.currency, self.subunits))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Overdraft):
            return self.currency == other.currency and self.subunits == other.subunits
        return NotImplemented

    def __gt__(self: Overdraft[C_co], other: Overdraft[C_co] | Money[C_co]) -> bool:
        if isinstance(other, Overdraft) and self.currency == other.currency:
            return self.subunits < other.subunits
        if isinstance(other, Money) and self.currency == other.currency:
            return False
        return NotImplemented

    def __ge__(self: Overdraft[C_co], other: Overdraft[C_co] | Money[C_co]) -> bool:
        if isinstance(other, Overdraft) and self.currency == other.currency:
            return self.subunits <= other.subunits
        if isinstance(other, Money) and self.currency == other.currency:
            return False
        return NotImplemented

    def __lt__(self: Overdraft[C_co], other: Overdraft[C_co] | Money[C_co]) -> bool:
        if isinstance(other, Overdraft) and self.currency == other.currency:
            return self.subunits > other.subunits
        if isinstance(other, Money) and self.currency == other.currency:
            return True
        return NotImplemented

    def __le__(self: Overdraft[C_co], other: Overdraft[C_co] | Money[C_co]) -> bool:
        if isinstance(other, Overdraft) and self.currency == other.currency:
            return self.subunits >= other.subunits
        if isinstance(other, Money) and self.currency == other.currency:
            return True
        return NotImplemented

    @overload
    def __add__(
        self: Overdraft[C_co],
        other: Money[C_co],
    ) -> Money[C_co] | Overdraft[C_co]: ...

    @overload
    def __add__(self: Overdraft[C_co], other: Overdraft[C_co]) -> Overdraft[C_co]: ...

    def __add__(self: Overdraft[C_co], other: object) -> Money[C_co] | Overdraft[C_co]:
        if isinstance(other, Overdraft) and self.currency == other.currency:
            return self.currency.overdraft_from_subunit(self.subunits + other.subunits)
        if isinstance(other, Money) and self.currency == other.currency:
            return _dispatch_type(other.subunits - self.subunits, self.currency)
        return NotImplemented

    def __radd__(
        self: Overdraft[C_co],
        other: Money[C_co],
    ) -> Money[C_co] | Overdraft[C_co]:
        return self.__add__(other)

    @overload
    def __sub__(self: Overdraft[C_co], other: Money[C_co]) -> Overdraft[C_co]: ...

    @overload
    def __sub__(
        self: Overdraft[C_co],
        other: Overdraft[C_co],
    ) -> Money[C_co] | Overdraft[C_co]: ...

    def __sub__(
        self: Overdraft[C_co],
        other: Money[C_co] | Overdraft[C_co],
    ) -> Money[C_co] | Overdraft[C_co]:
        if not isinstance(other, Money | Overdraft) or self.currency != other.currency:
            return NotImplemented

        value = (
            # This rewrite is equivalent to
            #   (-x) - (-y) == (-x) + y == y - x
            other.subunits - self.subunits
            if isinstance(other, Overdraft)
            # This rewrite is equivalent to
            # (-x) - y == -x - y == -(x + y)
            else -(self.subunits + other.subunits)
        )

        return _dispatch_type(value, self.currency)

    def __rsub__(self: Overdraft[C_co], other: Money[C_co]) -> Money[C_co]:
        if isinstance(other, Money) and self.currency == other.currency:
            # In the interpretation that an overdraft is a negative value, this is
            # equivalent to subtracting a negative value, which can be equivalently
            # rewritten as an addition (x - (-y) == x + y).
            return self.currency.from_subunit(self.subunits + other.subunits)
        return NotImplemented

    def __abs__(self: Overdraft[C_co]) -> Money[C_co]:
        return self.currency.from_subunit(self.subunits)

    def __neg__(self: Overdraft[C_co]) -> Money[C_co]:
        return self.currency.from_subunit(self.subunits)

    def __pos__(self: Overdraft[C_co]) -> Overdraft[C_co]:
        return self

    @overload
    def __mul__(self, other: int) -> Money[C_co] | Overdraft[C_co]: ...

    @overload
    def __mul__(self, other: Decimal) -> SubunitFraction[C_co]: ...

    @overload
    def __mul__(self, other: Fraction) -> SubunitFraction[C_co]: ...

    def __mul__(
        self,
        other: object,
    ) -> Money[C_co] | SubunitFraction[C_co] | Self:
        if isinstance(other, int):
            return _dispatch_type(-self.subunits * other, self.currency)
        if isinstance(other, Fraction):
            return SubunitFraction(-self.subunits * other, self.currency)
        if isinstance(other, Decimal):
            return SubunitFraction(-self.subunits * Fraction(other), self.currency)
        return NotImplemented

    @overload
    def __rmul__(self, other: int) -> Money[C_co] | Self: ...

    @overload
    def __rmul__(self, other: Decimal | Fraction) -> SubunitFraction[C_co]: ...

    def __rmul__(
        self,
        other: int | Decimal | Fraction,
    ) -> Money[C_co] | SubunitFraction[C_co] | Self:
        return self.__mul__(other)

    def __floordiv__(self, other: object) -> tuple[Self | Money[C_co], ...]:
        """
        Divides the original value over the numerator and returns a tuple of new
        Overdraft instances where the original value is spread as evenly as possible.
        The sum of the returned values will always equal the original value.

        Note that, because Overdraft cannot have a value of zero, this operation can
        return Money values. This only happens when a resulting chunk must equal zero.
        """
        if not isinstance(other, int):
            return NotImplemented

        over: Self | Money[C_co]

        try:
            over = self.currency.overdraft_from_subunit(self.subunits // other)
        except ZeroDivisionError as e:
            raise DivisionByZero from e
        except InvalidOverdraftValue:
            over = self.currency.from_subunit(0)

        under_subunit = over.subunits
        remainder = self.subunits - under_subunit * other
        under = self.currency.overdraft_from_subunit(under_subunit + 1)

        return (
            *(over for _ in range(other - remainder)),
            *(under for _ in range(remainder)),
        )

    @overload
    def __truediv__(self, other: int) -> SubunitFraction[C_co]: ...

    @overload
    def __truediv__(self, other: Fraction) -> SubunitFraction[C_co]: ...

    def __truediv__(self, other: object) -> SubunitFraction[C_co]:
        if not isinstance(other, int | Fraction):
            return NotImplemented
        if other == 0:
            raise DivisionByZero
        return SubunitFraction.from_overdraft(self, other)

    @overload
    def __rtruediv__(self, other: int) -> SubunitFraction[C_co]: ...

    @overload
    def __rtruediv__(self, other: Fraction) -> SubunitFraction[C_co]: ...

    def __rtruediv__(self, other: object) -> SubunitFraction[C_co]:
        if not isinstance(other, int | Fraction):
            return NotImplemented
        if other == 0:
            return SubunitFraction(0, self.currency)
        return 1 / SubunitFraction.from_overdraft(self, other)

    @classmethod
    # This needs HKT to allow typing to work properly for subclasses of Overdraft, that
    # would also allow moving the implementation to the shared super-class.
    def from_subunit(cls, value: int, currency: C_inv) -> Overdraft[C_inv]:
        return cls(
            subunits=value,
            currency=currency,
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
