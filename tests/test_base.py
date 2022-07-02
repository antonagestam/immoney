from __future__ import annotations

import random
from decimal import Decimal
from decimal import InvalidOperation
from fractions import Fraction
from typing import Any

import pytest
from abcattrs import UndefinedAbstractAttribute
from hypothesis import example
from hypothesis import given
from hypothesis.strategies import composite
from hypothesis.strategies import decimals
from hypothesis.strategies import integers
from hypothesis.strategies import text

from immoney import Currency
from immoney import Money
from immoney import Overdraft
from immoney import Round
from immoney import SubunitFraction
from immoney._base import valid_subunit
from immoney.currencies import NOK
from immoney.currencies import SEK
from immoney.currencies import SEKType
from immoney.errors import DivisionByZero
from immoney.errors import FrozenInstanceError
from immoney.errors import InvalidSubunit
from immoney.errors import MoneyParseError

max_valid_sek = 10_000_000_000_000_000_000_000_000 - 1
valid_sek = decimals(
    min_value=0,
    max_value=max_valid_sek,
    places=2,
    allow_nan=False,
    allow_infinity=False,
)
very_small_decimal = Decimal("0.0000000000000000000000000001")


@composite
def sums_to_valid_sek(
    draw,
    first_pick=valid_sek,
):
    a = draw(first_pick)
    return a, draw(
        decimals(
            min_value=0,
            max_value=max_valid_sek - a,
            places=2,
            allow_nan=False,
            allow_infinity=False,
        )
    )


@composite
def currencies(
    draw,
    code_values=text(max_size=3, min_size=3),
):
    class Subclass(Currency):
        subunit = random.choice(tuple(valid_subunit))
        code = draw(code_values)

    return Subclass()


class TestCurrency:
    def test_subclassing_with_missing_abstract_attribute_raises(self):
        with pytest.raises(UndefinedAbstractAttribute):
            type("sub", (Currency,), {"code": "foo"})

        with pytest.raises(UndefinedAbstractAttribute):
            type("sub", (Currency,), {"subunit": 1})

    def test_subclassing_with_invalid_subunit_raises_value_error(self):
        with pytest.raises(InvalidSubunit):
            type("sub", (Currency,), {"subunit": 2, "code": "foo"})

    @given(text())
    def test_str_representation_is_code(self, test_code: str):
        class Subclass(Currency):
            code = test_code
            subunit = 1

        instance = Subclass()

        assert str(instance) == test_code

    @given(valid_sek)
    def test_call_instantiates_money(self, value: Decimal):
        assert SEK(value) == Money(value, SEK)

    @given(name=text(), value=valid_sek | text())
    @example(name="code", value="USD")
    @example(name="subunit", value=1)
    def test_raises_on_assignment(self, name: str, value: object):
        initial = getattr(SEK, name, None)

        with pytest.raises(FrozenInstanceError):
            setattr(SEK, name, value)

        assert SEK.code == "SEK"
        assert SEK.subunit == 100
        assert initial == getattr(SEK, name, None)

    @pytest.mark.parametrize("subunit_value", valid_subunit)
    def test_decimal_exponent_is_width_of_subunit(self, subunit_value: int):
        class Subclass(Currency):
            code = "foo"
            subunit = subunit_value

        instance = Subclass()

        assert instance.decimal_exponent == Decimal(
            "0." + len(str(subunit_value)) * "0"
        )

    def test_zero_returns_cached_instance_of_money_zero(self):
        assert SEK.zero is SEK.zero
        assert SEK.zero.value == 0
        assert SEK.zero.currency is SEK

    @given(
        currency=currencies(),
        value=decimals(
            min_value=very_small_decimal, allow_nan=False, allow_infinity=False
        ),
    )
    @example(currency=SEK, value=Decimal("0.01"))
    def test_normalize_value_raises_for_precision_loss(
        self, currency: Currency, value: Decimal
    ):
        with pytest.raises(MoneyParseError):
            currency.normalize_value(value)
            currency.normalize_value(value + very_small_decimal)

    @given(
        currency=currencies(),
        value=integers(max_value=-1) | decimals(max_value=Decimal("-0.000001")),
    )
    def test_normalize_value_raises_for_negative_value(
        self, currency: Currency, value: object
    ):
        with pytest.raises(MoneyParseError):
            currency.normalize_value(value)  # type: ignore[arg-type]

    @given(currencies())
    def test_normalize_value_raises_for_invalid_str(self, currency: Currency):
        with pytest.raises(MoneyParseError):
            currency.normalize_value("foo")

    @given(currencies())
    def test_normalize_value_raises_for_nan(self, currency: Currency):
        with pytest.raises(MoneyParseError):
            currency.normalize_value(Decimal("nan"))


valid_values = decimals(
    min_value=0,
    max_value=100_000_000_000_000_000_000_000_000 - 1,
    allow_nan=False,
    allow_infinity=False,
)


@composite
def monies(
    draw,
    currencies=currencies(),
    values=valid_values,
):
    currency = draw(currencies)
    value = draw(values)
    fraction = SubunitFraction(Fraction(value), currency)
    return fraction.round(Round.DOWN)


class TestMoney:
    @given(valid_sek)
    @example(Decimal("1"))
    @example(Decimal("1.01"))
    @example(Decimal("1.010000"))
    def test_instantiation_normalizes_value(self, value: Decimal):
        instantiated = SEK(value)
        assert instantiated.value == value
        assert instantiated.value.as_tuple().exponent == -2

    @given(valid_sek)
    @example(Decimal("1"))
    @example(Decimal("1.01"))
    @example(Decimal("1.010000"))
    def test_instantiation_caches_instances(self, value: Decimal):
        assert SEK(value) is SEK(value)

    def test_cannot_instantiate_subunit_fraction(self):
        with pytest.raises(MoneyParseError):
            SEK(Decimal("1.001"))

    def test_raises_type_error_when_instantiated_with_non_currency(self):
        with pytest.raises(TypeError):
            Money("2.00", "SEK")  # type: ignore[type-var]

    @given(money=monies(), name=text(), value=valid_sek | text())
    @example(SEK(23), "value", Decimal("123"))
    @example(NOK(23), "currency", SEK)
    def test_raises_on_assignment(self, money: Money[Any], name: str, value: object):
        initial = getattr(money, name, None)
        with pytest.raises(FrozenInstanceError):
            setattr(money, name, value)
        assert getattr(money, name, None) == initial

    @pytest.mark.parametrize(
        ("value", "expected"),
        (
            (SEK("523.12"), "Money('523.12', SEK)"),
            (SEK("52"), "Money('52.00', SEK)"),
            (SEK("0"), "Money('0.00', SEK)"),
            (NOK(8000), "Money('8000.00', NOK)"),
        ),
    )
    def test_repr(self, value: Money[Any], expected: str):
        assert expected == repr(value)

    def test_hash(self):
        a = SEK(23)
        b = NOK(23)
        assert hash(a) != hash(b)
        mapped = {a: "a", b: "b"}
        assert mapped[a] == "a"
        assert mapped[b] == "b"
        assert {a, a, b} == {a, b, b}
        assert hash(SEK(13)) == hash(SEK(13))

    def test_can_check_equality_with_zero(self):
        assert SEK(0) == 0
        assert 0 == SEK(0)
        assert SEK("0.01") != 0
        assert 0 != SEK("0.01")
        assert NOK(0) == 0
        assert 0 == NOK(0)
        assert NOK("0.01") != 0
        assert 0 != NOK("0.01")

    @given(value=monies(), number=integers(min_value=1))
    @example(SEK(1), 1)
    @example(SEK("0.1"), 1)
    @example(SEK("0.01"), 1)
    def test_cannot_check_equality_with_non_zero(self, value: Money[Any], number: int):
        assert value != number

    @given(value=valid_sek)
    def test_can_check_equality_with_instance(self, value: Decimal):
        instance = SEK(value)
        assert instance == SEK(value)
        next_plus = SEK.from_subunit(instance.as_subunit() + 1)
        assert next_plus != value
        assert value != next_plus

        other_currency = NOK(value)
        assert other_currency != instance
        assert instance != other_currency
        assert other_currency != next_plus
        assert next_plus != other_currency

    @given(a=monies(), b=monies())
    @example(NOK(0), SEK(0))
    @example(SEK(0), NOK(0))
    @example(SEK(10), NOK(10))
    def test_never_equal_across_currencies(self, a: Money[Any], b: Money[Any]):
        assert a != b

    @given(valid_sek, valid_sek)
    @example(0, 0)
    @example(1, 1)
    @example(1, 0)
    @example(0, 1)
    def test_total_ordering_within_currency(self, x: Decimal | int, y: Decimal | int):
        a = SEK(x)
        b = SEK(y)
        assert (a > b and b < a) or (a < b and b > a) or (a == b and b == a)
        assert (a >= b and b <= a) or (a <= b and b >= a)

    @given(a=monies(), b=monies())
    @example(NOK(0), SEK(0))
    @example(SEK(1), NOK(2))
    def test_raises_type_error_for_ordering_across_currencies(
        self,
        a: Money[Any],
        b: Money[Any],
    ):
        with pytest.raises(TypeError):
            a > b  # noqa: B015
        with pytest.raises(TypeError):
            a >= b  # noqa: B015
        with pytest.raises(TypeError):
            a < b  # noqa: B015
        with pytest.raises(TypeError):
            a <= b  # noqa: B015
        with pytest.raises(TypeError):
            b > a  # noqa: B015
        with pytest.raises(TypeError):
            b >= a  # noqa: B015
        with pytest.raises(TypeError):
            b < a  # noqa: B015
        with pytest.raises(TypeError):
            b <= a  # noqa: B015

    @given(sums_to_valid_sek())
    @example((Decimal(0), Decimal(0)))
    def test_add(self, xy: tuple[Decimal, Decimal]):
        x, y = xy
        a = SEK(x)
        b = SEK(y)
        assert (b + a).value == (a + b).value == (x + y)

    @given(a=monies(), b=monies())
    @example(NOK(0), SEK(0))
    @example(SEK(1), NOK(2))
    def test_raises_type_error_for_addition_across_currencies(
        self,
        a: Money[Any],
        b: Money[Any],
    ):
        with pytest.raises(TypeError):
            a + b
        with pytest.raises(TypeError):
            b + a

    @given(sums_to_valid_sek())
    @example((Decimal(0), Decimal(0)))
    def test_iadd(self, xy: tuple[Decimal, Decimal]):
        x, y = xy
        a = SEK(x)
        b = SEK(y)
        c = a
        c += b
        d = b
        d += a
        assert c.value == d.value == (x + y)

    @given(a=monies(), b=monies())
    @example(NOK(0), SEK(0))
    @example(SEK(1), NOK(2))
    def test_raises_type_error_for_inline_addition_across_currencies(
        self,
        a: Money[Any],
        b: Money[Any],
    ):
        with pytest.raises(TypeError):
            a += b
        with pytest.raises(TypeError):
            b += a

    @given(monies())
    def test_pos(self, a: Money[Any]):
        assert +a == a

    @given(sums_to_valid_sek())
    @example((Decimal(0), Decimal(0)))
    def test_sub(self, xy: tuple[Decimal, Decimal]):
        x, y = sorted(xy, reverse=True)
        a = SEK(x)
        b = SEK(y)

        if a == b:
            assert a - b == b - a == 0
            return

        expected_sum = x - y

        pos = a - b
        assert isinstance(pos, Money)
        assert pos.value == expected_sum

        neg = b - a
        assert isinstance(neg, Overdraft)
        assert neg.money.value == expected_sum

    @given(a=monies(), b=monies())
    @example(NOK(0), SEK(0))
    @example(SEK(1), NOK(2))
    def test_raises_type_error_for_subtraction_across_currencies(
        self,
        a: Money[Any],
        b: Money[Any],
    ):
        with pytest.raises(TypeError):
            a - b
        with pytest.raises(TypeError):
            b - a

    @given(monies())
    def test_neg(self, a: Money[Any]):
        negged = -a
        assert isinstance(negged, Overdraft)
        assert negged.money == a
        assert +a == a

    @given(monies(), integers(min_value=0))
    def test_returns_instance_when_multiplied_with_positive_integer(
        self,
        a: Money[Any],
        b: int,
    ):
        expected_product = a.value * b
        try:
            product = a * b
        except InvalidOperation:
            assert expected_product * a.currency.subunit > max_valid_sek
            return
        assert isinstance(product, Money)
        assert product.currency is a.currency
        assert product.value == expected_product
        reverse_applied = b * a
        assert isinstance(reverse_applied, Money)
        assert reverse_applied.currency is a.currency
        assert reverse_applied.value == expected_product

    @given(monies(), integers(max_value=-1))
    def test_returns_overdraft_when_multiplied_with_negative_integer(
        self,
        a: Money[Any],
        b: int,
    ):
        expected_product = -a.value * b
        try:
            product = a * b
        except InvalidOperation:
            assert expected_product * a.currency.subunit > max_valid_sek
            return
        assert isinstance(product, Overdraft)
        assert product.money.currency is a.currency
        assert product.money.value == expected_product
        reverse_applied = b * a
        assert isinstance(reverse_applied, Overdraft)
        assert reverse_applied.money.currency is a.currency
        assert reverse_applied.money.value == expected_product

    @given(monies(), decimals(allow_infinity=False, allow_nan=False))
    def test_returns_subunit_fraction_when_multiplied_with_decimal(
        self,
        a: Money[Any],
        b: Decimal,
    ):
        try:
            product = a * b
        except InvalidOperation:
            return
        assert isinstance(product, SubunitFraction)
        assert product.currency is a.currency
        assert product.value == Fraction(a.value) * Fraction(b) * Fraction(
            a.currency.subunit
        )
        reverse_applied = b * a
        assert isinstance(reverse_applied, SubunitFraction)
        assert reverse_applied.currency is a.currency
        assert reverse_applied.value == product.value

    @given(valid_sek, valid_sek)
    def test_raises_type_error_for_multiplication_between_instances(
        self, x: Decimal, y: Decimal
    ):
        a = SEK(x)
        b = SEK(y)
        with pytest.raises(TypeError):
            a * b  # type: ignore[operator]
        with pytest.raises(TypeError):
            b * a  # type: ignore[operator]

    @pytest.mark.parametrize("value", [object(), 1.0, str(), {}])
    def test_raises_type_error_for_truediv_with_non_integer_value(self, value: object):
        with pytest.raises(TypeError):
            SEK(1) / value

    @given(valid_sek, integers(min_value=1, max_value=500))
    def test_returns_evenly_divided_parts_on_integer_truediv(
        self, dividend_value: Decimal, divisor: int
    ):
        dividend = SEK(dividend_value)
        quotient = dividend / divisor

        # The number of parts the value is divided among is equal to divisor.
        assert len(quotient) == divisor
        # The sum of all the returned parts are equal to the dividend.
        assert sum(quotient, SEK.zero) == dividend
        # The returned parts differ at most by 1 subunit.
        assert max(quotient) - min(quotient) in (0, SEK.one_subunit)
        # The returned parts are sorted in descending order.
        assert sorted(quotient, reverse=True) == list(quotient)

    @given(valid_sek)
    def test_raises_division_by_zero_on_truediv_with_zero(self, value: Decimal):
        non_zero = SEK(value) + SEK.one_subunit
        with pytest.raises(DivisionByZero):
            non_zero / 0

    # to test:
    # -> truediv
    # floordiv
