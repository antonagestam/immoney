from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
from typing import Any

import pytest
from hypothesis import assume
from hypothesis import example
from hypothesis import given
from hypothesis.strategies import integers
from hypothesis.strategies import just
from hypothesis.strategies import text
from typing_extensions import assert_type

from immoney import Currency
from immoney import Money
from immoney import Overdraft
from immoney import SubunitFraction
from immoney._base import ParsableMoneyValue
from immoney.currencies import NOK
from immoney.currencies import SEK
from immoney.currencies import SEKType
from immoney.errors import DivisionByZero
from immoney.errors import FrozenInstanceError
from immoney.errors import InvalidOverdraftValue
from immoney.errors import ParseError

from .strategies import currencies
from .strategies import monies
from .strategies import overdrafts
from .strategies import valid_money_subunits
from .strategies import valid_overdraft_subunits
from .strategies import valid_sek_decimals


@given(valid_sek_decimals)
@example(Decimal("1"))
@example(Decimal("1.01"))
@example(Decimal("1.010000"))
def test_instantiation_normalizes_value(value: Decimal) -> None:
    assume(value != 0)
    instantiated = SEK.overdraft(value)
    assert instantiated.decimal == value
    assert instantiated.decimal.as_tuple().exponent == -2


@pytest.mark.parametrize("value", (0, "0.00", Decimal(0), Decimal("0.0")))
def test_raises_type_error_for_value_zero(value: ParsableMoneyValue) -> None:
    with pytest.raises(
        InvalidOverdraftValue,
        match=(
            r"^Overdraft cannot be instantiated with a value of zero, the Money "
            r"class should be used instead\.$"
        ),
    ):
        SEK.overdraft(value)


def test_instantiation_caches_instance() -> None:
    assert SEK.overdraft("1.01") is SEK.overdraft("1.010")
    assert SEK.overdraft(1) is SEK.overdraft(1)


def test_cannot_instantiate_subunit_fraction() -> None:
    with pytest.raises(ParseError):
        SEK.overdraft(Decimal("1.001"))


def test_raises_type_error_when_instantiated_with_non_currency() -> None:
    with pytest.raises(TypeError):
        Overdraft("2.00", "SEK")  # type: ignore[call-overload]


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
        (SEK.overdraft(Decimal("523.12")), "Overdraft('523.12', SEK)"),
        (SEK.overdraft(52), "Overdraft('52.00', SEK)"),
        (SEK.overdraft(Decimal("52.13")), "Overdraft('52.13', SEK)"),
        (SEK.overdraft("0.01"), "Overdraft('0.01', SEK)"),
        (NOK.overdraft(8000), "Overdraft('8000.00', NOK)"),
    ),
)
def test_repr(value: SubunitFraction[Any], expected: str) -> None:
    assert expected == repr(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    (
        (SEK.overdraft("523.12"), "-523.12\xa0SEK"),
        (SEK.overdraft("52"), "-52.00\xa0SEK"),
        (SEK.overdraft("0.01"), "-0.01\xa0SEK"),
        (SEK.overdraft("0.49"), "-0.49\xa0SEK"),
        (SEK.overdraft("0.99"), "-0.99\xa0SEK"),
        (SEK.overdraft("99.99"), "-99.99\xa0SEK"),
        (NOK.overdraft(8000), "-8000.00\xa0NOK"),
    ),
)
def test_str(value: Money[Any], expected: str) -> None:
    assert expected == str(value)


def test_hash() -> None:
    a = SEK.overdraft(23)
    b = NOK.overdraft(23)
    assert hash(a) != hash(b)
    mapped = {a: "a", b: "b"}
    assert mapped[a] == "a"
    assert mapped[b] == "b"
    assert {a, a, b} == {a, b, b}
    assert hash(SEK.overdraft(13)) == hash(SEK.overdraft(13))


class TestOrdering:
    def test_can_check_equality_with_zero(self) -> None:
        assert SEK.overdraft("0.01") != 0
        assert 0 != SEK.overdraft("0.01")
        assert NOK.overdraft("0.01") != 0
        assert 0 != NOK.overdraft("0.01")

    @given(value=overdrafts(), number=integers(min_value=1))
    @example(SEK.overdraft(1), 1)
    @example(SEK.overdraft("0.1"), 1)
    @example(SEK.overdraft("0.01"), 1)
    def test_cannot_check_equality_with_non_zero(
        self,
        value: Overdraft[Currency],
        number: int,
    ) -> None:
        assert value != number

    @given(value=valid_overdraft_subunits)
    def test_can_check_equality_with_instance(self, value: int) -> None:
        instance = SEK.overdraft_from_subunit(value)
        assert instance == SEK.overdraft_from_subunit(value)
        next_plus = SEK.overdraft_from_subunit(instance.subunits + 1)
        assert next_plus != value
        assert value != next_plus

        other_currency = NOK.overdraft_from_subunit(value)
        assert other_currency != instance
        assert instance != other_currency
        assert other_currency != next_plus
        assert next_plus != other_currency

    @given(a=overdrafts(), b=overdrafts())
    @example(NOK.overdraft(1), SEK.overdraft(1))
    @example(SEK.overdraft(1), NOK.overdraft(1))
    @example(SEK.overdraft(10), NOK.overdraft(10))
    def test_never_equal_across_currencies(
        self,
        a: Overdraft[Currency],
        b: Overdraft[Currency],
    ) -> None:
        assert a != b

    @given(valid_overdraft_subunits, valid_overdraft_subunits)
    @example(1, 1)
    @example(2, 1)
    @example(1, 2)
    def test_total_ordering_within_currency(self, x: int, y: int) -> None:
        a = SEK.overdraft_from_subunit(x)
        b = SEK.overdraft_from_subunit(y)
        assert (a > b and b < a) or (a < b and b > a) or (a == b and b == a)
        assert (a >= b and b <= a) or (a <= b and b >= a)

    @given(a=overdrafts(), b=overdrafts() | monies())
    @example(NOK.overdraft(1), SEK.overdraft(1))
    @example(SEK.overdraft(1), NOK.overdraft(2))
    def test_raises_type_error_for_ordering_across_currencies(
        self,
        a: Overdraft[Currency],
        b: Overdraft[Currency] | Money[Currency],
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

    @given(monies(currencies=just(SEK)), overdrafts(currencies=just(SEK)))
    def test_always_strictly_less_than_money(
        self,
        money: Money[SEKType],
        overdraft: Overdraft[SEKType],
    ) -> None:
        assert money > overdraft
        assert money >= overdraft
        assert not (money < overdraft)
        assert not (money <= overdraft)


@given(overdrafts())
def test_abs_returns_money(value: Overdraft[Any]) -> None:
    assert abs(value) is value.currency.from_subunit(value.subunits)


@given(overdrafts())
def test_neg_returns_money(value: Overdraft[Any]) -> None:
    assert -value is value.currency.from_subunit(value.subunits)


@given(overdrafts())
def test_pos_returns_self(value: Overdraft[Any]) -> None:
    assert value is +value


def test_can_check_equality_with_zero() -> None:
    assert SEK.overdraft("0.01") != 0
    assert 0 != SEK.overdraft("0.01")
    assert NOK.overdraft("0.01") != 0
    assert 0 != NOK.overdraft("0.01")


@given(value=overdrafts(), number=integers(min_value=1))
@example(SEK(1), 1)
@example(SEK("0.1"), 1)
@example(SEK("0.01"), 1)
def test_equality_with_non_zero_is_always_false(
    value: Overdraft[Any],
    number: int,
) -> None:
    assert value != number


@given(money_value=monies(), overdraft_value=overdrafts())
@example(SEK(1), SEK.overdraft(1))
def test_equality_with_money_is_always_false(
    money_value: Money[Any],
    overdraft_value: Overdraft[Any],
) -> None:
    assert money_value != overdraft_value
    assert overdraft_value != money_value


@given(valid_overdraft_subunits, valid_overdraft_subunits)
@example(1, 1)
def test_can_add_instances(x: int, y: int) -> None:
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
    x: int,
    y: int,
) -> None:
    a = SEK.overdraft(x)
    b = NOK.overdraft(y)
    with pytest.raises(TypeError):
        a + b  # type: ignore[operator]
    with pytest.raises(TypeError):
        b + a  # type: ignore[operator]


@given(valid_overdraft_subunits, valid_money_subunits)
def test_adding_money_equals_subtraction(x: int, y: int) -> None:
    assume(x != 0)
    a = SEK.overdraft_from_subunit(x)
    b = SEK.from_subunit(y)
    assert abs(a + b).subunits == abs(b + a).subunits == abs(x - y)


def test_can_add_money() -> None:
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
    x: int,
    y: int,
) -> None:
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
def test_cannot_add_arbitrary_object(value: object) -> None:
    with pytest.raises(TypeError):
        SEK.overdraft(1) + value  # type: ignore[operator]

    with pytest.raises(TypeError):
        value + SEK.overdraft(1)  # type: ignore[operator]


@given(valid_overdraft_subunits, valid_overdraft_subunits)
@example(1, 1)
def test_can_subtract_instances(x: int, y: int) -> None:
    a = SEK.overdraft_from_subunit(x)
    b = SEK.overdraft_from_subunit(y)
    assert abs(b - a).subunits == abs(a - b).subunits == abs(x - y)


@given(valid_overdraft_subunits, valid_overdraft_subunits)
@example(1, 1)
def test_subtracting_instances_of_different_currency_raises_type_error(
    x: int,
    y: int,
) -> None:
    a = SEK.overdraft_from_subunit(x)
    b = NOK.overdraft_from_subunit(y)
    with pytest.raises(TypeError):
        a - b  # type: ignore[operator]
    with pytest.raises(TypeError):
        b - a  # type: ignore[operator]


@given(valid_overdraft_subunits, valid_money_subunits)
@example(1, 0)
def test_subtracting_money_equals_addition(x: int, y: int) -> None:
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
    a: Money[SEKType] | Overdraft[SEKType],
    b: Money[SEKType] | Overdraft[SEKType],
    expected_difference: Money[SEKType] | Overdraft[SEKType],
) -> None:
    assert a - b == expected_difference


@given(valid_money_subunits, valid_overdraft_subunits)
def test_subtracting_money_of_different_currency_raises_type_error(
    x: int,
    y: int,
) -> None:
    a = SEK(x)
    b = NOK.overdraft(y)
    with pytest.raises(TypeError):
        a - b  # type: ignore[operator]
    with pytest.raises(TypeError):
        b - a  # type: ignore[operator]


@pytest.mark.parametrize(
    "value", (object(), 0, 1, 0.0, 2.3, Decimal("0.0"), Decimal(3), [], ())
)
def test_cannot_subtract_arbitrary_object(value: object) -> None:
    with pytest.raises(TypeError):
        SEK.overdraft(1) - value  # type: ignore[operator]

    with pytest.raises(TypeError):
        value - SEK.overdraft(1)  # type: ignore[operator]


@given(currencies(), integers(min_value=1))
@example(SEK, 1)
def test_subunit_roundtrip(currency: Currency, value: int) -> None:
    assert value == Overdraft.from_subunit(value, currency).subunits


class TestMul:
    @pytest.mark.parametrize(
        ("a", "b", "expected_result"),
        [
            (SEK.overdraft("12.34"), 2, SEK.overdraft("24.68")),
            (SEK.overdraft("12.34"), -2, SEK("24.68")),
            (SEK.overdraft(10), Decimal("0.5"), SEK.fraction(-500)),
            (SEK.overdraft(10), Decimal("-0.5"), SEK.fraction(500)),
            (SEK.overdraft(10), Fraction(1, 2), SEK.fraction(-500)),
            (SEK.overdraft(10), Fraction(-1, 2), SEK.fraction(500)),
        ],
    )
    def test_can_multiply(
        self,
        a: Overdraft[SEKType],
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
            (SEK.overdraft(3), SEK.overdraft(3)),
            (SEK.overdraft(1), SEK(1)),
            (SEK.overdraft(1), NOK.overdraft(1)),
            (SEK.overdraft(1), object()),
        ),
    )
    def test_raises_type_error_for_invalid_other(
        self,
        a: Overdraft[Currency],
        b: object,
    ) -> None:
        with pytest.raises(
            TypeError,
            match=r"^unsupported operand type\(s\) for \*: 'Overdraft' and",
        ):
            a * b  # type: ignore[operator]
        with pytest.raises(
            TypeError,
            match=(r"^unsupported operand type\(s\) for \*: '(\w+)' and 'Overdraft'$"),
        ):
            b * a  # type: ignore[operator]


class TestTruediv:
    @pytest.mark.parametrize(
        ("a", "b", "expected"),
        [
            (SEK.overdraft("0.75"), 2, SEK.fraction(-75, 2)),
            (SEK.overdraft("0.75"), -2, SEK.fraction(75, 2)),
            (SEK.overdraft("0.75"), Fraction(1, 3), SEK.fraction(-225)),
            (SEK.overdraft("0.75"), Fraction(-1, 3), SEK.fraction(225)),
        ],
    )
    def test_can_truediv(
        self,
        a: Overdraft[SEKType],
        b: int | Fraction,
        expected: SubunitFraction[SEKType],
    ) -> None:
        assert_type(a / b, SubunitFraction[SEKType])
        assert a / b == expected

    @pytest.mark.parametrize(
        ("a", "b", "expected"),
        [
            (2, SEK.overdraft("0.75"), SEK.fraction(-2, 75)),
            (-2, SEK.overdraft("0.75"), SEK.fraction(2, 75)),
            (Fraction(1, 3), SEK.overdraft("0.75"), SEK.fraction(-1, 225)),
            (Fraction(-1, 3), SEK.overdraft("0.75"), SEK.fraction(1, 225)),
            (0, SEK.overdraft("0.75"), SEK.fraction(0)),
        ],
    )
    def test_can_rtruediv(
        self,
        a: int | Fraction,
        b: Overdraft[SEKType],
        expected: SubunitFraction[SEKType],
    ) -> None:
        assert_type(a / b, SubunitFraction[SEKType])
        assert a / b == expected

    @pytest.mark.parametrize(
        ("a", "b"),
        (
            (SEK.overdraft(3), SEK.overdraft(3)),
            (SEK.overdraft(1), SEK(1)),
            (SEK.overdraft(1), NOK.overdraft(1)),
            (SEK.overdraft(1), object()),
        ),
    )
    def test_raises_type_error_for_invalid_other(
        self,
        a: Overdraft[Currency],
        b: object,
    ) -> None:
        with pytest.raises(
            TypeError,
            match=r"^unsupported operand type\(s\) for /: 'Overdraft' and",
        ):
            a / b  # type: ignore[operator]
        with pytest.raises(
            TypeError,
            match=(r"^unsupported operand type\(s\) for /: '(\w+)' and 'Overdraft'$"),
        ):
            b / a  # type: ignore[operator]

    def test_raises_division_by_zero(self) -> None:
        with pytest.raises(DivisionByZero):
            SEK.overdraft(1) / 0
