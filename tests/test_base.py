from __future__ import annotations

import random
from decimal import Decimal
from decimal import InvalidOperation
from fractions import Fraction
from typing import Any

import pytest
from abcattrs import UndefinedAbstractAttribute
from hypothesis import assume
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
from immoney._base import ParsableMoneyValue
from immoney._base import valid_subunit
from immoney.currencies import NOK
from immoney.currencies import SEK
from immoney.currencies import SEKType
from immoney.errors import DivisionByZero
from immoney.errors import FrozenInstanceError
from immoney.errors import InvalidOverdraftValue
from immoney.errors import InvalidSubunit
from immoney.errors import ParseError

from .strategies import valid_money_subunits
from .strategies import valid_overdraft_subunits
from .strategies import valid_sek_decimals

very_small_decimal = Decimal("0.0000000000000000000000000001")


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

    @given(valid_sek_decimals)
    def test_call_instantiates_money(self, value: int):
        assert SEK(value) == Money(value, SEK)

    @given(name=text(), value=valid_money_subunits | text())
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

    def test_zero_returns_cached_instance_of_money_zero(self) -> None:
        assert SEK.zero is SEK.zero
        assert SEK.zero.subunits == 0
        assert SEK.zero.currency is SEK

    def test_normalize_value_raises_for_precision_loss(self) -> None:
        with pytest.raises(ParseError):
            SEK.normalize_to_subunits(Decimal("0.01") + very_small_decimal)

    @given(
        value=integers(max_value=-1) | decimals(max_value=Decimal("-0.000001")),
    )
    def test_normalize_value_raises_for_negative_value(self, value: object) -> None:
        with pytest.raises(ParseError):
            SEK.normalize_to_subunits(value)

    def test_normalize_value_raises_for_invalid_str(self) -> None:
        with pytest.raises(ParseError):
            SEK.normalize_to_subunits("foo")

    def test_normalize_value_raises_for_nan(self) -> None:
        with pytest.raises(ParseError):
            SEK.normalize_to_subunits(Decimal("nan"))

    def test_normalize_value_raises_for_non_finite(self) -> None:
        with pytest.raises(ParseError):
            SEK.normalize_to_subunits(Decimal("inf"))

    def test_normalize_value_raises_for_invalid_type(self) -> None:
        with pytest.raises(NotImplementedError):
            SEK.normalize_to_subunits(float("inf"))

    def test_from_subunit_returns_money_instance(self) -> None:
        instance = SEK.from_subunit(100)
        assert isinstance(instance, Money)
        assert instance.subunits == 100
        assert instance.decimal == Decimal("1.00")
        assert instance.currency is SEK

    def test_overdraft_from_subunit_returns_overdraft_instance(self) -> None:
        instance = SEK.overdraft_from_subunit(100)
        assert isinstance(instance, Overdraft)
        assert instance.subunits == 100
        assert instance.decimal == Decimal("1.00")
        assert instance.currency is SEK


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
    subunits=integers(min_value=0),
) -> Money[Currency]:
    return Money.from_subunit(draw(subunits), draw(currencies))


@composite
def overdrafts(
    draw,
    currencies=currencies(),
    subunits=integers(min_value=1),
) -> Overdraft[Currency]:
    return Overdraft.from_subunit(draw(subunits), draw(currencies))


class TestMoney:
    @given(valid_sek_decimals)
    @example(Decimal("1"))
    @example(Decimal("1.01"))
    @example(Decimal("1.010000"))
    # This value identifies a case where improperly using floats to represent
    # intermediate values, will lead to precision loss in the .decimal property.
    @example(Decimal("132293239054008.35"))
    def test_instantiation_normalizes_decimal(self, value: Decimal):
        instantiated = SEK(value)
        assert instantiated.decimal == value
        assert instantiated.decimal.as_tuple().exponent == -2

    def test_instantiation_caches_instance(self):
        assert SEK("1.01") is SEK("1.010")
        assert SEK(1) is SEK(1)

    def test_cannot_instantiate_subunit_fraction(self):
        with pytest.raises(ParseError):
            SEK(Decimal("1.001"))

    def test_raises_type_error_when_instantiated_with_non_currency(self):
        with pytest.raises(TypeError):
            Money("2.00", "SEK")  # type: ignore[call-overload]

    def test_raises_type_error_when_instantiated_with_invalid_args(self):
        with pytest.raises(TypeError):
            Money(foo=1, bar=2)  # type: ignore[call-overload]

    @given(money=monies(), name=text(), value=valid_sek_decimals | text())
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

    @given(value=valid_sek_decimals)
    def test_can_check_equality_with_instance(self, value: Decimal):
        instance = SEK(value)
        assert instance == SEK(value)
        next_plus = SEK.from_subunit(instance.subunits + 1)
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

    @given(valid_money_subunits, valid_money_subunits)
    @example(0, 0)
    @example(1, 1)
    @example(1, 0)
    @example(0, 1)
    def test_total_ordering_within_currency(self, x: int, y: int):
        a = SEK.from_subunit(x)
        b = SEK.from_subunit(y)
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

    @given(integers(min_value=0), integers(min_value=0))
    @example(0, 0)
    def test_add(self, x: int, y: int):
        a = SEK.from_subunit(x)
        b = SEK.from_subunit(y)
        assert (b + a).subunits == (a + b).subunits == (x + y)

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

    @given(valid_money_subunits, valid_money_subunits)
    def test_iadd(self, x: int, y: int):
        a = SEK.from_subunit(x)
        b = SEK.from_subunit(y)
        c = a
        c += b
        d = b
        d += a
        assert c.subunits == d.subunits == (x + y)

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
    def test_pos_returns_self(self, a: Money[Any]):
        assert +a is a

    @given(monies())
    def test_abs_returns_self(self, value: Money[Any]):
        assert value is abs(value)

    @given(overdrafts())
    def test_neg_returns_overdraft(self, overdraft: Overdraft[Any]):
        value = Money.from_subunit(overdraft.subunits, overdraft.currency)
        assert -value is overdraft

    def test_neg_zero_returns_self(self):
        value = SEK(0)
        assert -value is value

    @given(valid_money_subunits, valid_money_subunits)
    def test_sub(self, x: int, y: int):
        x, y = sorted((x, y), reverse=True)
        a = SEK.from_subunit(x)
        b = SEK.from_subunit(y)

        if a == b:
            assert a - b == b - a == 0
            return

        expected_sum = x - y

        pos = a - b
        assert isinstance(pos, Money)
        assert pos.subunits == expected_sum

        neg = b - a
        assert isinstance(neg, Overdraft)
        assert neg.subunits == expected_sum

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
        assume(a.subunits != 0)
        negged = -a
        assert isinstance(negged, Overdraft)
        assert negged.subunits == a.subunits
        assert negged.currency == a.currency
        assert -negged is a
        assert +a is a

    @given(monies(), integers(min_value=0))
    def test_returns_instance_when_multiplied_with_positive_integer(
        self,
        a: Money[Any],
        b: int,
    ):
        expected_product = a.subunits * b
        product = a * b
        assert isinstance(product, Money)
        assert product.currency is a.currency
        assert product.subunits == expected_product
        reverse_applied = b * a
        assert isinstance(reverse_applied, Money)
        assert reverse_applied.currency is a.currency
        assert reverse_applied.subunits == expected_product

    @given(monies(), integers(max_value=-1))
    def test_returns_overdraft_when_multiplied_with_negative_integer(
        self,
        a: Money[Any],
        b: int,
    ):
        assume(a.subunits != 0)

        expected_product = -a.subunits * b
        product = a * b
        assert isinstance(product, Overdraft)
        assert product.currency is a.currency
        assert product.subunits == expected_product
        reverse_applied = b * a
        assert isinstance(reverse_applied, Overdraft)
        assert reverse_applied.currency is a.currency
        assert reverse_applied.subunits == expected_product

    @given(integers(), currencies())
    def test_multiplying_with_zero_returns_money_zero(self, a: int, currency: Currency):
        zero = currency(0)
        result = a * zero

        assert isinstance(result, Money)
        assert result.subunits == 0
        assert result.currency == currency

        # Test commutative property.
        assert zero * a == result

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
        assert product.value == Fraction(a.subunits) * Fraction(b)
        reverse_applied = b * a
        assert isinstance(reverse_applied, SubunitFraction)
        assert reverse_applied.currency is a.currency
        assert reverse_applied.value == product.value

    @given(valid_money_subunits, valid_money_subunits)
    @example(0, 0)
    def test_raises_type_error_for_multiplication_between_instances(
        self,
        x: int,
        y: int,
    ):
        a = SEK(x)
        b = SEK(y)
        with pytest.raises(TypeError):
            a * b  # type: ignore[operator]
        with pytest.raises(TypeError):
            b * a  # type: ignore[operator]

    @pytest.mark.parametrize("value", [object(), 1.0, "", {}])
    def test_raises_type_error_for_floordiv_with_invalid_denominator(
        self, value: object
    ):
        with pytest.raises(TypeError):
            SEK(1) // value

    @given(monies(), integers(min_value=1, max_value=500))
    def test_returns_evenly_divided_parts_on_integer_floordiv(
        self,
        dividend: Money[Any],
        divisor: int,
    ):
        currency = dividend.currency
        quotient = dividend // divisor

        # The number of parts the value is divided among is equal to divisor.
        assert len(quotient) == divisor
        # The sum of all the returned parts are equal to the dividend.
        assert sum(quotient, currency.zero) == dividend
        # The returned parts differ at most by 1 subunit.
        assert max(quotient) - min(quotient) in (0, currency.one_subunit)
        # The returned parts are sorted in descending order.
        assert sorted(quotient, reverse=True) == list(quotient)

    @given(monies())
    def test_raises_division_by_zero_on_floordiv_with_zero(self, value: Money[Any]):
        non_zero = value + value.currency.one_subunit
        with pytest.raises(DivisionByZero):
            non_zero // 0

    @pytest.mark.parametrize("value", [object(), 1.0, Decimal("1.0"), {}])
    def test_raises_type_error_for_truediv_with_invalid_denominator(
        self, value: object
    ):
        with pytest.raises(TypeError):
            SEK(1) / value  # type: ignore[operator]

    @given(monies(), integers(min_value=1))
    def test_returns_subunit_fraction_on_truediv(
        self, dividend: Money[Any], divisor: int
    ):
        quotient = dividend / divisor

        assert isinstance(quotient, SubunitFraction)
        assert quotient.value == Fraction(dividend.subunits, divisor)
        assert quotient.currency == dividend.currency

    @given(monies())
    def test_raises_division_by_zero_on_truediv_with_zero(self, value: Money[Any]):
        non_zero = value + value.currency.one_subunit
        with pytest.raises(DivisionByZero):
            non_zero / 0
        with pytest.raises(DivisionByZero):
            non_zero / Fraction()

    def test_as_subunit_returns_value_as_subunit_integer(self):
        class FooType(Currency):
            code = "foo"
            subunit = 10_000

        Foo = FooType()

        one_subunit = Foo("0.0001")
        assert one_subunit.subunits == 1

        one_main_unit = Foo(1)
        assert one_main_unit.subunits == Foo.subunit

    def test_from_subunit_returns_instance(self):
        class FooType(Currency):
            code = "foo"
            subunit = 10_000

        Foo = FooType()

        one_subunit = Money.from_subunit(1, Foo)
        assert one_subunit == Foo("0.0001")

        one_main_unit = Money.from_subunit(Foo.subunit, Foo)
        assert one_main_unit == Foo(1)

    @given(currencies(), integers(min_value=0))
    @example(SEK, 1)
    def test_subunit_roundtrip(self, currency: Currency, value: int):
        assert value == Money.from_subunit(value, currency).subunits

    def test_floored_returns_closest_currency_value(self):
        assert Money.floored(Decimal("0.001"), SEK) == SEK(0)
        assert Money.floored(Decimal("0.009"), SEK) == SEK(0)
        assert Money.floored(Decimal("0.010"), SEK) == SEK("0.01")
        assert Money.floored(Decimal("0.019"), SEK) == SEK("0.01")
        assert Money.floored(Decimal("-0.001"), SEK) == SEK(0)

    def test_floored_raises_for_invalid_value(self):
        with pytest.raises(ParseError):
            Money.floored(Decimal("-0.0101"), SEK)


class TestSubunitFraction:
    def test_init_normalizes_value(self):
        instance = SubunitFraction(Decimal("123.15"), SEK)
        assert isinstance(instance.value, Fraction)
        assert instance.value == Fraction(12315, 100)

    def test_init_raises_for_invalid_value(self):
        with pytest.raises(ValueError):
            SubunitFraction("foo", SEK)  # type: ignore[arg-type]

    def test_init_raises_for_invalid_currency(self):
        with pytest.raises(TypeError):
            SubunitFraction(Decimal("123.15"), 123)  # type: ignore[type-var]

    def test_init_caches_instance(self):
        a = SubunitFraction(Decimal("152.15"), SEK)
        b = SubunitFraction(Decimal("152.15"), SEK)
        c = SubunitFraction(Decimal("152.16"), SEK)
        assert a is b
        assert b is a
        assert a is not c
        assert c is not a
        assert b is not c
        assert c is not b

    @pytest.mark.parametrize(
        ("value", "expected"),
        (
            (SEK.fraction(Decimal("523.1234")), "SubunitFraction('2615617/5000', SEK)"),
            (SEK.fraction(52), "SubunitFraction('52', SEK)"),
            (SEK.fraction(Decimal("52.13")), "SubunitFraction('5213/100', SEK)"),
            (SEK.fraction(0), "SubunitFraction('0', SEK)"),
            (NOK.fraction(8000), "SubunitFraction('8000', NOK)"),
        ),
    )
    def test_repr(self, value: SubunitFraction[Any], expected: str):
        assert expected == repr(value)

    def test_hash(self):
        a = SEK.fraction(23)
        b = NOK.fraction(23)
        assert hash(a) != hash(b)
        mapped = {a: "a", b: "b"}
        assert mapped[a] == "a"
        assert mapped[b] == "b"
        assert {a, a, b} == {a, b, b}
        assert hash(SEK.fraction(13)) == hash(SEK.fraction(13))

    def test_can_check_equality_with_zero(self):
        assert SEK.fraction(0) == 0
        assert 0 == SEK.fraction(0)
        assert SEK.fraction(1) != 0
        assert 0 != SEK.fraction(1)
        assert NOK.fraction(0) == 0
        assert 0 == NOK.fraction(0)
        assert NOK.fraction(1) != 0
        assert 0 != NOK.fraction(1)

    @given(value=monies(), number=integers(min_value=1))
    @example(SEK(1), 1)
    @example(SEK("0.1"), 1)
    @example(SEK("0.01"), 1)
    def test_cannot_check_equality_with_non_zero(self, value: Money[Any], number: int):
        assert SubunitFraction.from_money(value) != number

    def test_equality(self):
        zero = SubunitFraction(0, SEK)
        one = SubunitFraction(100, SEK)
        assert zero == zero
        assert one == one
        assert zero != one
        assert one != zero

        different_one = SubunitFraction(100, NOK)
        assert one != different_one
        assert different_one != one

        money_one = SEK(1)
        assert money_one == one
        assert one == money_one
        assert money_one != zero
        assert zero != money_one
        assert money_one != different_one
        assert different_one != money_one

        overdraft_one = SEK.overdraft(1)
        assert overdraft_one == -one
        assert one == -overdraft_one
        assert overdraft_one != zero
        assert zero != overdraft_one
        assert overdraft_one != -different_one
        assert different_one != -overdraft_one

    def test_from_money_returns_instance(self):
        class FooType(Currency):
            code = "foo"
            subunit = 10_000

        Foo = FooType()

        one_subunit = SubunitFraction.from_money(Foo("0.0001"))
        assert one_subunit == SubunitFraction(1, Foo)

        one_main_unit = SubunitFraction.from_money(Foo(1))
        assert one_main_unit == SubunitFraction(10_000, Foo)

    def test_round_money_returns_money(self):
        fraction = SubunitFraction(Fraction(997, 3), SEK)
        assert SEK("3.32") == fraction.round_money(Round.DOWN)
        assert SEK("3.33") == fraction.round_money(Round.UP)
        assert SEK("3.32") == fraction.round_money(Round.HALF_UP)
        assert SEK("3.32") == fraction.round_money(Round.HALF_EVEN)
        assert SEK("3.32") == fraction.round_money(Round.HALF_DOWN)

    def test_round_money_raises_parser_error_for_negative_fraction(self):
        with pytest.raises(ParseError):
            SubunitFraction(-1, SEK).round_money(Round.DOWN)

        with pytest.raises(ParseError):
            SubunitFraction(-100, NOK).round_money(Round.DOWN)

    def test_round_overdraft_returns_overdraft(self):
        fraction = SubunitFraction(Fraction(-997, 3), SEK)
        assert SEK.overdraft("3.33") == fraction.round_overdraft(Round.DOWN)
        assert SEK.overdraft("3.32") == fraction.round_overdraft(Round.UP)
        assert SEK.overdraft("3.32") == fraction.round_overdraft(Round.HALF_UP)
        assert SEK.overdraft("3.32") == fraction.round_overdraft(Round.HALF_EVEN)
        assert SEK.overdraft("3.32") == fraction.round_overdraft(Round.HALF_DOWN)

    def test_round_overdraft_raises_parse_error_for_positive_fraction(self):
        with pytest.raises(ParseError):
            SubunitFraction(1, SEK).round_overdraft(Round.DOWN)

    def test_round_either_returns_overdraft_for_negative_fraction(self):
        fraction = SubunitFraction(Fraction(-997, 3), SEK)
        assert SEK.overdraft("3.33") == fraction.round_either(Round.DOWN)
        assert SEK.overdraft("3.32") == fraction.round_either(Round.UP)
        assert SEK.overdraft("3.32") == fraction.round_either(Round.HALF_UP)
        assert SEK.overdraft("3.32") == fraction.round_either(Round.HALF_EVEN)
        assert SEK.overdraft("3.32") == fraction.round_either(Round.HALF_DOWN)

    def test_round_either_returns_money_for_positive_fraction(self):
        fraction = SubunitFraction(Fraction(997, 3), SEK)
        assert SEK("3.32") == fraction.round_either(Round.DOWN)
        assert SEK("3.33") == fraction.round_either(Round.UP)
        assert SEK("3.32") == fraction.round_either(Round.HALF_UP)
        assert SEK("3.32") == fraction.round_either(Round.HALF_EVEN)
        assert SEK("3.32") == fraction.round_either(Round.HALF_DOWN)


class TestOverdraft:
    @given(valid_sek_decimals)
    @example(Decimal("1"))
    @example(Decimal("1.01"))
    @example(Decimal("1.010000"))
    def test_instantiation_normalizes_value(self, value: Decimal):
        assume(value != 0)
        instantiated = SEK.overdraft(value)
        assert instantiated.decimal == value
        assert instantiated.decimal.as_tuple().exponent == -2

    @pytest.mark.parametrize("value", (0, "0.00", Decimal(0), Decimal("0.0")))
    def test_raises_type_error_for_value_zero(self, value: ParsableMoneyValue):
        with pytest.raises(
            InvalidOverdraftValue,
            match=(
                r"^Overdraft cannot be instantiated with a value of zero, the Money "
                r"class should be used instead\.$"
            ),
        ):
            SEK.overdraft(value)

    def test_instantiation_caches_instance(self):
        assert SEK.overdraft("1.01") is SEK.overdraft("1.010")
        assert SEK.overdraft(1) is SEK.overdraft(1)

    def test_cannot_instantiate_subunit_fraction(self):
        with pytest.raises(ParseError):
            SEK.overdraft(Decimal("1.001"))

    def test_raises_type_error_when_instantiated_with_non_currency(self):
        with pytest.raises(TypeError):
            Overdraft("2.00", "SEK")  # type: ignore[call-overload]

    @given(money=monies(), name=text(), value=valid_sek_decimals | text())
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
            (SEK.overdraft(Decimal("523.12")), "Overdraft('523.12', SEK)"),
            (SEK.overdraft(52), "Overdraft('52.00', SEK)"),
            (SEK.overdraft(Decimal("52.13")), "Overdraft('52.13', SEK)"),
            (SEK.overdraft("0.01"), "Overdraft('0.01', SEK)"),
            (NOK.overdraft(8000), "Overdraft('8000.00', NOK)"),
        ),
    )
    def test_repr(self, value: SubunitFraction[Any], expected: str):
        assert expected == repr(value)

    def test_hash(self):
        a = SEK.overdraft(23)
        b = NOK.overdraft(23)
        assert hash(a) != hash(b)
        mapped = {a: "a", b: "b"}
        assert mapped[a] == "a"
        assert mapped[b] == "b"
        assert {a, a, b} == {a, b, b}
        assert hash(SEK.overdraft(13)) == hash(SEK.overdraft(13))

    @given(overdrafts())
    def test_abs_returns_money(self, value: Overdraft[Any]):
        assert abs(value) is value.currency.from_subunit(value.subunits)

    @given(overdrafts())
    def test_neg_returns_money(self, value: Overdraft[Any]):
        assert -value is value.currency.from_subunit(value.subunits)

    @given(overdrafts())
    def test_pos_returns_self(self, value: Overdraft[Any]):
        assert value is +value

    def test_can_check_equality_with_zero(self):
        assert SEK.overdraft("0.01") != 0
        assert 0 != SEK.overdraft("0.01")
        assert NOK.overdraft("0.01") != 0
        assert 0 != NOK.overdraft("0.01")

    @given(value=overdrafts(), number=integers(min_value=1))
    @example(SEK(1), 1)
    @example(SEK("0.1"), 1)
    @example(SEK("0.01"), 1)
    def test_equality_with_non_zero_is_always_false(
        self, value: Overdraft[Any], number: int
    ):
        assert value != number

    @given(money_value=monies(), overdraft_value=overdrafts())
    @example(SEK(1), SEK.overdraft(1))
    def test_equality_with_money_is_always_false(
        self,
        money_value: Money[Any],
        overdraft_value: Overdraft[Any],
    ):
        assert money_value != overdraft_value
        assert overdraft_value != money_value

    @given(valid_overdraft_subunits, valid_overdraft_subunits)
    @example(1, 1)
    def test_can_add_instances(self, x: int, y: int):
        a = SEK.overdraft_from_subunit(x)
        b = SEK.overdraft_from_subunit(y)

        # Test commutative property.
        c = b + a
        assert isinstance(c, Overdraft)
        d = a + b
        assert isinstance(d, Overdraft)
        assert c == d
        assert c.subunits == d.subunits == x + y

    @given(valid_overdraft_subunits, valid_overdraft_subunits)
    @example(1, 1)
    def test_adding_instances_of_different_currency_raises_type_error(
        self,
        x: int,
        y: int,
    ):
        a = SEK.overdraft(x)
        b = NOK.overdraft(y)
        with pytest.raises(TypeError):
            a + b  # type: ignore[operator]
        with pytest.raises(TypeError):
            b + a  # type: ignore[operator]

    @given(valid_overdraft_subunits, valid_money_subunits)
    def test_adding_money_equals_subtraction(self, x: int, y: int):
        assume(x != 0)
        a = SEK.overdraft_from_subunit(x)
        b = SEK.from_subunit(y)
        assert abs(a + b).subunits == abs(b + a).subunits == abs(x - y)

    def test_can_add_money(self):
        a = SEK.from_subunit(1000)
        b = SEK.overdraft_from_subunit(600)
        positive_sum = a + b
        assert isinstance(positive_sum, Money)
        assert positive_sum.decimal == Decimal("4.00")
        assert positive_sum.subunits == 400
        assert positive_sum == b + a

        c = SEK.from_subunit(600)
        d = SEK.overdraft_from_subunit(1000)
        negative_sum = c + d
        assert isinstance(negative_sum, Overdraft)
        assert negative_sum.decimal == Decimal("4.00")
        assert negative_sum.subunits == 400
        assert negative_sum == d + c

    @given(valid_money_subunits, valid_overdraft_subunits)
    @example(0, 1)
    def test_adding_money_of_different_currency_raises_type_error(
        self,
        x: int,
        y: int,
    ):
        a = SEK(x)
        assume(y != 0)
        b = NOK.overdraft(y)
        with pytest.raises(TypeError):
            a + b  # type: ignore[operator]
        with pytest.raises(TypeError):
            b + a  # type: ignore[operator]

    @pytest.mark.parametrize(
        "value", (object(), 0, 1, 0.0, 2.3, Decimal("0.0"), Decimal(3), [], ())
    )
    def test_cannot_add_arbitrary_object(self, value: object):
        with pytest.raises(TypeError):
            SEK.overdraft(1) + value  # type: ignore[operator]

        with pytest.raises(TypeError):
            value + SEK.overdraft(1)  # type: ignore[operator]

    @given(valid_overdraft_subunits, valid_overdraft_subunits)
    @example(1, 1)
    def test_can_subtract_instances(self, x: int, y: int):
        a = SEK.overdraft_from_subunit(x)
        b = SEK.overdraft_from_subunit(y)
        assert abs(b - a).subunits == abs(a - b).subunits == abs(x - y)

    @given(valid_overdraft_subunits, valid_overdraft_subunits)
    @example(1, 1)
    def test_subtracting_instances_of_different_currency_raises_type_error(
        self,
        x: int,
        y: int,
    ):
        a = SEK.overdraft_from_subunit(x)
        b = NOK.overdraft_from_subunit(y)
        with pytest.raises(TypeError):
            a - b  # type: ignore[operator]
        with pytest.raises(TypeError):
            b - a  # type: ignore[operator]

    @given(valid_overdraft_subunits, valid_money_subunits)
    @example(1, 0)
    def test_subtracting_money_equals_addition(self, x: int, y: int):
        a = SEK.overdraft_from_subunit(x)
        b = SEK.from_subunit(y)
        assert abs(a - b).subunits == abs(b - a).subunits == abs(x + y)

    @pytest.mark.parametrize(
        "a, b, expected_difference",
        [
            (SEK(1000), SEK.overdraft(600), SEK(1600)),
            (SEK(600), SEK.overdraft(1000), SEK(1600)),
            (SEK.overdraft(600), SEK(1000), SEK.overdraft(1600)),
            (SEK.overdraft(1000), SEK(600), SEK.overdraft(1600)),
        ],
    )
    def test_can_subtract_money(
        self,
        a: Money[SEKType] | Overdraft[SEKType],
        b: Money[SEKType] | Overdraft[SEKType],
        expected_difference: Money[SEKType] | Overdraft[SEKType],
    ):
        assert a - b == expected_difference

    @given(valid_money_subunits, valid_overdraft_subunits)
    def test_subtracting_money_of_different_currency_raises_type_error(
        self,
        x: int,
        y: int,
    ):
        a = SEK(x)
        b = NOK.overdraft(y)
        with pytest.raises(TypeError):
            a - b  # type: ignore[operator]
        with pytest.raises(TypeError):
            b - a  # type: ignore[operator]

    @pytest.mark.parametrize(
        "value", (object(), 0, 1, 0.0, 2.3, Decimal("0.0"), Decimal(3), [], ())
    )
    def test_cannot_subtract_arbitrary_object(self, value: object):
        with pytest.raises(TypeError):
            SEK.overdraft(1) - value  # type: ignore[operator]

        with pytest.raises(TypeError):
            value - SEK.overdraft(1)  # type: ignore[operator]

    @given(currencies(), integers(min_value=1))
    @example(SEK, 1)
    def test_subunit_roundtrip(self, currency: Currency, value: int):
        assert value == Overdraft.from_subunit(value, currency).subunits
