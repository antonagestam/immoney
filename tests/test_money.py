from __future__ import annotations

from decimal import Decimal
from decimal import InvalidOperation
from fractions import Fraction
from typing import Any

import pytest
from hypothesis import assume
from hypothesis import example
from hypothesis import given
from hypothesis.strategies import decimals
from hypothesis.strategies import integers
from hypothesis.strategies import text
from typing_extensions import assert_type

from immoney import Currency
from immoney import Money
from immoney import Overdraft
from immoney import SubunitFraction
from immoney.currencies import NOK
from immoney.currencies import SEK
from immoney.currencies import SEKType
from immoney.errors import DivisionByZero
from immoney.errors import FrozenInstanceError
from immoney.errors import ParseError

from .strategies import currencies
from .strategies import monies
from .strategies import overdrafts
from .strategies import valid_money_subunits
from .strategies import valid_sek_decimals


@given(valid_sek_decimals)
@example(Decimal("1"))
@example(Decimal("1.01"))
@example(Decimal("1.010000"))
# This value identifies a case where improperly using floats to represent
# intermediate values, will lead to precision loss in the .decimal property.
@example(Decimal("132293239054008.35"))
def test_instantiation_normalizes_decimal(value: Decimal) -> None:
    instantiated = SEK(value)
    assert instantiated.decimal == value
    assert instantiated.decimal.as_tuple().exponent == -2


def test_instantiation_caches_instance() -> None:
    assert SEK("1.01") is SEK("1.010")
    assert SEK(1) is SEK(1)


def test_cannot_instantiate_subunit_fraction() -> None:
    with pytest.raises(ParseError):
        SEK(Decimal("1.001"))


def test_raises_type_error_when_instantiated_with_non_currency() -> None:
    with pytest.raises(TypeError):
        Money("2.00", "SEK")  # type: ignore[call-overload]


def test_raises_type_error_when_instantiated_with_invalid_args() -> None:
    with pytest.raises(TypeError):
        Money(foo=1, bar=2)  # type: ignore[call-overload]


@given(money=monies(), name=text(), value=valid_sek_decimals | text())
@example(SEK(23), "value", Decimal("123"))
@example(NOK(23), "currency", SEK)
def test_raises_on_assignment(money: Money[Any], name: str, value: object) -> None:
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
        (SEK("0.01"), "Money('0.01', SEK)"),
        (SEK("0.49"), "Money('0.49', SEK)"),
        (SEK("0.99"), "Money('0.99', SEK)"),
        (SEK("99.99"), "Money('99.99', SEK)"),
        (NOK(8000), "Money('8000.00', NOK)"),
    ),
)
def test_repr(value: Money[Any], expected: str) -> None:
    assert expected == repr(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    (
        (SEK("523.12"), "523.12\xa0SEK"),
        (SEK("52"), "52.00\xa0SEK"),
        (SEK("0"), "0.00\xa0SEK"),
        (SEK("0.01"), "0.01\xa0SEK"),
        (SEK("0.49"), "0.49\xa0SEK"),
        (SEK("0.99"), "0.99\xa0SEK"),
        (SEK("99.99"), "99.99\xa0SEK"),
        (NOK(8000), "8000.00\xa0NOK"),
    ),
)
def test_str(value: Money[Any], expected: str) -> None:
    assert expected == str(value)


def test_hash() -> None:
    a = SEK(23)
    b = NOK(23)
    assert hash(a) != hash(b)
    mapped = {a: "a", b: "b"}
    assert mapped[a] == "a"
    assert mapped[b] == "b"
    assert {a, a, b} == {a, b, b}
    assert hash(SEK(13)) == hash(SEK(13))


def test_can_check_equality_with_zero() -> None:
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
def test_cannot_check_equality_with_non_zero(value: Money[Any], number: int) -> None:
    assert value != number


@given(value=valid_sek_decimals)
def test_can_check_equality_with_instance(value: Decimal) -> None:
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
def test_never_equal_across_currencies(a: Money[Any], b: Money[Any]) -> None:
    assert a != b


@given(valid_money_subunits, valid_money_subunits)
@example(0, 0)
@example(1, 1)
@example(1, 0)
@example(0, 1)
def test_total_ordering_within_currency(x: int, y: int) -> None:
    a = SEK.from_subunit(x)
    b = SEK.from_subunit(y)
    assert (a > b and b < a) or (a < b and b > a) or (a == b and b == a)
    assert (a >= b and b <= a) or (a <= b and b >= a)


@given(a=monies(), b=monies())
@example(NOK(0), SEK(0))
@example(SEK(1), NOK(2))
def test_raises_type_error_for_ordering_across_currencies(
    a: Money[Any],
    b: Money[Any],
) -> None:
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
def test_add(x: int, y: int) -> None:
    a = SEK.from_subunit(x)
    b = SEK.from_subunit(y)
    assert (b + a).subunits == (a + b).subunits == (x + y)


@given(a=monies(), b=monies())
@example(NOK(0), SEK(0))
@example(SEK(1), NOK(2))
def test_raises_type_error_for_addition_across_currencies(
    a: Money[Any],
    b: Money[Any],
) -> None:
    with pytest.raises(TypeError):
        a + b
    with pytest.raises(TypeError):
        b + a


@given(valid_money_subunits, valid_money_subunits)
def test_iadd(x: int, y: int) -> None:
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
    a: Money[Any],
    b: Money[Any],
) -> None:
    with pytest.raises(TypeError):
        a += b
    with pytest.raises(TypeError):
        b += a


@given(monies())
def test_pos_returns_self(a: Money[Any]) -> None:
    assert +a is a


@given(monies())
def test_abs_returns_self(value: Money[Any]) -> None:
    assert value is abs(value)


@given(overdrafts())
def test_neg_returns_overdraft(overdraft: Overdraft[Any]) -> None:
    value = Money.from_subunit(overdraft.subunits, overdraft.currency)
    assert -value is overdraft


def test_neg_zero_returns_self() -> None:
    value = SEK(0)
    assert -value is value


@given(valid_money_subunits, valid_money_subunits)
def test_sub(x: int, y: int) -> None:
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
    a: Money[Any],
    b: Money[Any],
) -> None:
    with pytest.raises(TypeError):
        a - b
    with pytest.raises(TypeError):
        b - a


@given(monies())
def test_neg(a: Money[Any]) -> None:
    assume(a.subunits != 0)
    negged = -a
    assert isinstance(negged, Overdraft)
    assert negged.subunits == a.subunits
    assert negged.currency == a.currency
    assert -negged is a
    assert +a is a


@given(monies(), integers(min_value=0))
def test_returns_instance_when_multiplied_with_positive_integer(
    a: Money[Any],
    b: int,
) -> None:
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
    a: Money[Any],
    b: int,
) -> None:
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
def test_multiplying_with_zero_returns_money_zero(a: int, currency: Currency) -> None:
    zero = currency(0)
    result = a * zero

    assert isinstance(result, Money)
    assert result.subunits == 0
    assert result.currency == currency

    # Test commutative property.
    assert zero * a == result


@given(monies(), decimals(allow_infinity=False, allow_nan=False))
def test_returns_subunit_fraction_when_multiplied_with_decimal(
    a: Money[Any],
    b: Decimal,
) -> None:
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
    x: int,
    y: int,
) -> None:
    a = SEK(x)
    b = SEK(y)
    with pytest.raises(TypeError):
        a * b  # type: ignore[operator]
    with pytest.raises(TypeError):
        b * a  # type: ignore[operator]


@pytest.mark.parametrize("value", [object(), 1.0, "", {}])
def test_raises_type_error_for_floordiv_with_invalid_denominator(value: object) -> None:
    with pytest.raises(TypeError):
        SEK(1) // value


@given(monies(), integers(min_value=1, max_value=500))
def test_returns_evenly_divided_parts_on_integer_floordiv(
    dividend: Money[Any],
    divisor: int,
) -> None:
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
def test_raises_division_by_zero_on_floordiv_with_zero(value: Money[Any]) -> None:
    non_zero = value + value.currency.one_subunit
    with pytest.raises(DivisionByZero):
        non_zero // 0


@pytest.mark.parametrize("value", [object(), 1.0, Decimal("1.0"), {}])
def test_raises_type_error_for_truediv_with_invalid_denominator(value: object) -> None:
    with pytest.raises(TypeError):
        SEK(1) / value  # type: ignore[operator]


@given(monies(), integers(min_value=1))
def test_returns_subunit_fraction_on_truediv(
    dividend: Money[Any],
    divisor: int,
) -> None:
    quotient = dividend / divisor

    assert isinstance(quotient, SubunitFraction)
    assert quotient.value == Fraction(dividend.subunits, divisor)
    assert quotient.currency == dividend.currency


@given(monies())
def test_raises_division_by_zero_on_truediv_with_zero(value: Money[Any]) -> None:
    non_zero = value + value.currency.one_subunit
    with pytest.raises(DivisionByZero):
        non_zero / 0
    with pytest.raises(DivisionByZero):
        non_zero / Fraction()


def test_as_subunit_returns_value_as_subunit_integer() -> None:
    class FooType(Currency):
        code = "foo"
        subunit = 10_000

    Foo = FooType()

    one_subunit = Foo("0.0001")
    assert one_subunit.subunits == 1

    one_main_unit = Foo(1)
    assert one_main_unit.subunits == Foo.subunit


def test_from_subunit_returns_instance() -> None:
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
def test_subunit_roundtrip(currency: Currency, value: int) -> None:
    assert value == Money.from_subunit(value, currency).subunits


class TestMul:
    @pytest.mark.parametrize(
        ("a", "b", "expected_result"),
        [
            (SEK("12.34"), 2, SEK("24.68")),
            (SEK("12.34"), -2, SEK.overdraft("24.68")),
            (SEK(10), Decimal("0.5"), SEK.fraction(500)),
            (SEK(10), Decimal("-0.5"), SEK.fraction(-500)),
            (SEK(10), Fraction(1, 2), SEK.fraction(500)),
            (SEK(10), Fraction(-1, 2), SEK.fraction(-500)),
        ],
    )
    def test_can_multiply(
        self,
        a: Money[SEKType],
        b: int | Decimal | Fraction,
        expected_result: Money[SEKType] | Overdraft[SEKType] | SubunitFraction[SEKType],
    ) -> None:
        assert_type(
            a * b, Money[SEKType] | Overdraft[SEKType] | SubunitFraction[SEKType]
        )
        assert_type(
            b * a, Money[SEKType] | Overdraft[SEKType] | SubunitFraction[SEKType]
        )
        assert a * b == expected_result
        assert b * a == expected_result

    @pytest.mark.parametrize(
        ("a", "b"),
        (
            (SEK(3), SEK.overdraft(3)),
            (SEK(1), SEK(1)),
            (SEK(1), NOK.overdraft(1)),
            (SEK(1), object()),
        ),
    )
    def test_raises_type_error_for_invalid_other(
        self,
        a: Money[Currency],
        b: object,
    ) -> None:
        with pytest.raises(
            TypeError,
            match=r"^unsupported operand type\(s\) for \*: 'Money' and",
        ):
            a * b  # type: ignore[operator]
        with pytest.raises(
            TypeError,
            match=r"^unsupported operand type\(s\) for \*: '(\w+)' and 'Money'$",
        ):
            b * a  # type: ignore[operator]
