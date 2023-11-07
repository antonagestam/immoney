from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
from typing import Any

import pytest
from hypothesis import example
from hypothesis import given
from hypothesis.strategies import integers
from typing_extensions import assert_type

from immoney import Currency
from immoney import Money
from immoney import Overdraft
from immoney import Round
from immoney import SubunitFraction
from immoney.currencies import NOK
from immoney.currencies import SEK
from immoney.currencies import SEKType
from immoney.errors import ParseError

from .strategies import SEKMonetary
from .strategies import currencies
from .strategies import monies
from .strategies import overdrafts
from .strategies import sek_monetaries
from .strategies import subunit_fractions


def test_init_normalizes_value() -> None:
    instance = SubunitFraction(Decimal("123.15"), SEK)
    assert isinstance(instance.value, Fraction)
    assert instance.value == Fraction(12315, 100)


def test_init_raises_for_invalid_value() -> None:
    with pytest.raises(ValueError):
        SubunitFraction("foo", SEK)  # type: ignore[arg-type]


def test_init_raises_for_invalid_currency() -> None:
    with pytest.raises(TypeError):
        SubunitFraction(Decimal("123.15"), 123)  # type: ignore[type-var]


def test_init_caches_instance() -> None:
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
def test_repr(value: SubunitFraction[Any], expected: str) -> None:
    assert expected == repr(value)


def test_hash() -> None:
    a = SEK.fraction(23)
    b = NOK.fraction(23)
    assert hash(a) != hash(b)
    mapped = {a: "a", b: "b"}
    assert mapped[a] == "a"
    assert mapped[b] == "b"
    assert {a, a, b} == {a, b, b}
    assert hash(SEK.fraction(13)) == hash(SEK.fraction(13))


def test_can_check_equality_with_zero() -> None:
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
def test_cannot_check_equality_with_non_zero(value: Money[Any], number: int) -> None:
    assert SubunitFraction.from_money(value) != number


def test_equality() -> None:
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


@given(monies())
def test_compares_equal_to_same_currency_money(money: Money[Currency]) -> None:
    fraction = money.currency.fraction(money.subunits)
    assert fraction == money
    assert money == fraction
    assert fraction >= money
    assert fraction <= money
    assert money >= fraction
    assert money <= fraction


@given(overdrafts())
def test_compares_equal_to_same_currency_overdraft(
    overdraft: Overdraft[Currency],
) -> None:
    fraction = overdraft.currency.fraction(-overdraft.subunits)
    assert fraction == overdraft
    assert overdraft == fraction
    assert fraction >= overdraft
    assert fraction <= overdraft
    assert overdraft >= fraction
    assert overdraft <= fraction


@given(monies(), currencies())
def test_compares_unequal_to_differing_currency_money(
    money: Money[Currency],
    currency: Currency,
) -> None:
    fraction = currency.fraction(money.subunits)
    assert fraction != money
    assert money != fraction


@given(monies(), currencies())
def test_compares_unequal_to_differing_currency_overdraft(
    overdraft: Overdraft[Currency],
    currency: Currency,
) -> None:
    fraction = currency.fraction(overdraft.subunits)
    assert fraction != overdraft
    assert overdraft != fraction


def test_compares_unequal_across_values() -> None:
    fraction = SEK.fraction(99, 100)
    money = SEK(1)
    assert fraction != money
    assert money != fraction
    overdraft = SEK.overdraft(1)
    assert fraction != overdraft
    assert overdraft != fraction


def test_from_money_returns_instance() -> None:
    class FooType(Currency):
        code = "foo"
        subunit = 10_000

    Foo = FooType()

    one_subunit = SubunitFraction.from_money(Foo("0.0001"))
    assert one_subunit == SubunitFraction(1, Foo)

    one_main_unit = SubunitFraction.from_money(Foo(1))
    assert one_main_unit == SubunitFraction(10_000, Foo)


def test_round_money_returns_money() -> None:
    fraction = SubunitFraction(Fraction(997, 3), SEK)
    assert SEK("3.32") == fraction.round_money(Round.DOWN)
    assert SEK("3.33") == fraction.round_money(Round.UP)
    assert SEK("3.32") == fraction.round_money(Round.HALF_UP)
    assert SEK("3.32") == fraction.round_money(Round.HALF_EVEN)
    assert SEK("3.32") == fraction.round_money(Round.HALF_DOWN)


def test_round_money_raises_parser_error_for_negative_fraction() -> None:
    with pytest.raises(ParseError):
        SubunitFraction(-1, SEK).round_money(Round.DOWN)

    with pytest.raises(ParseError):
        SubunitFraction(-100, NOK).round_money(Round.DOWN)


def test_round_overdraft_returns_overdraft() -> None:
    fraction = SubunitFraction(Fraction(-997, 3), SEK)
    assert SEK.overdraft("3.33") == fraction.round_overdraft(Round.DOWN)
    assert SEK.overdraft("3.32") == fraction.round_overdraft(Round.UP)
    assert SEK.overdraft("3.32") == fraction.round_overdraft(Round.HALF_UP)
    assert SEK.overdraft("3.32") == fraction.round_overdraft(Round.HALF_EVEN)
    assert SEK.overdraft("3.32") == fraction.round_overdraft(Round.HALF_DOWN)


def test_round_overdraft_raises_parse_error_for_positive_fraction() -> None:
    with pytest.raises(ParseError):
        SubunitFraction(1, SEK).round_overdraft(Round.DOWN)


def test_round_either_returns_overdraft_for_negative_fraction() -> None:
    fraction = SubunitFraction(Fraction(-997, 3), SEK)
    assert SEK.overdraft("3.33") == fraction.round_either(Round.DOWN)
    assert SEK.overdraft("3.32") == fraction.round_either(Round.UP)
    assert SEK.overdraft("3.32") == fraction.round_either(Round.HALF_UP)
    assert SEK.overdraft("3.32") == fraction.round_either(Round.HALF_EVEN)
    assert SEK.overdraft("3.32") == fraction.round_either(Round.HALF_DOWN)


def test_round_either_returns_money_for_positive_fraction() -> None:
    fraction = SubunitFraction(Fraction(997, 3), SEK)
    assert SEK("3.32") == fraction.round_either(Round.DOWN)
    assert SEK("3.33") == fraction.round_either(Round.UP)
    assert SEK("3.32") == fraction.round_either(Round.HALF_UP)
    assert SEK("3.32") == fraction.round_either(Round.HALF_EVEN)
    assert SEK("3.32") == fraction.round_either(Round.HALF_DOWN)


class TestAdd:
    @pytest.mark.parametrize(
        ("a", "b", "expected"),
        [
            (
                SubunitFraction(Fraction(1, 2), SEK),
                SubunitFraction(Fraction(1, 4), SEK),
                SubunitFraction(Fraction(3, 4), SEK),
            ),
            (
                SubunitFraction(Fraction(997, 3), SEK),
                SubunitFraction(Fraction(13, 17), SEK),
                SubunitFraction(Fraction(16988, 51), SEK),
            ),
            (
                SubunitFraction(Fraction(997, 3), SEK),
                SEK("0.01"),
                SubunitFraction(Fraction(1000, 3), SEK),
            ),
            (
                SubunitFraction(Fraction(997, 3), SEK),
                SEK.overdraft("0.01"),
                SubunitFraction(Fraction(994, 3), SEK),
            ),
        ],
    )
    def test_can_add(
        self,
        a: SubunitFraction[SEKType],
        b: SubunitFraction[SEKType] | Money[SEKType] | Overdraft[SEKType],
        expected: SubunitFraction[SEKType],
    ) -> None:
        assert_type(a + b, SubunitFraction[SEKType])
        assert_type(b + a, SubunitFraction[SEKType])
        assert a + b == expected
        assert b + a == expected

    @pytest.mark.parametrize(
        ("a", "b"),
        (
            (
                SubunitFraction(Fraction(997, 3), SEK),
                SubunitFraction(Fraction(997, 3), NOK),
            ),
            (SubunitFraction(Fraction(997, 3), SEK), NOK(1)),
            (SubunitFraction(Fraction(997, 3), SEK), NOK.overdraft(1)),
            (SubunitFraction(Fraction(997, 3), SEK), 1),
        ),
    )
    def test_raises_type_error_for_invalid_other(
        self,
        a: SubunitFraction[Currency],
        b: object,
    ) -> None:
        with pytest.raises(
            TypeError,
            match=r"^unsupported operand type\(s\) for \+: 'SubunitFraction' and",
        ):
            a + b  # type: ignore[operator]
        with pytest.raises(
            TypeError,
            match=(
                r"^unsupported operand type\(s\) for \+: '(\w+)' and 'SubunitFraction'$"
            ),
        ):
            b + a  # type: ignore[operator]


class TestSub:
    @pytest.mark.parametrize(
        ("a", "b", "expected"),
        [
            (
                SubunitFraction(Fraction(3, 4), SEK),
                SubunitFraction(Fraction(1, 2), SEK),
                SubunitFraction(Fraction(1, 4), SEK),
            ),
            (
                SubunitFraction(Fraction(16988, 51), SEK),
                SubunitFraction(Fraction(997, 3), SEK),
                SubunitFraction(Fraction(13, 17), SEK),
            ),
            (
                SubunitFraction(Fraction(1000, 3), SEK),
                SEK("0.01"),
                SubunitFraction(Fraction(997, 3), SEK),
            ),
            (
                SubunitFraction(Fraction(994, 3), SEK),
                SEK.overdraft("0.01"),
                SubunitFraction(Fraction(997, 3), SEK),
            ),
        ],
    )
    def test_can_subtract(
        self,
        a: SubunitFraction[SEKType],
        b: SubunitFraction[SEKType] | Money[SEKType] | Overdraft[SEKType],
        expected: SubunitFraction[SEKType],
    ) -> None:
        c = a - b
        assert_type(c, SubunitFraction[SEKType])
        assert c == expected

        assert_type(a - c, SubunitFraction[SEKType])
        assert a - c == b

    @pytest.mark.parametrize(
        ("a", "b"),
        (
            (
                SubunitFraction(Fraction(997, 3), SEK),
                SubunitFraction(Fraction(997, 3), NOK),
            ),
            (SubunitFraction(Fraction(997, 3), SEK), NOK(1)),
            (SubunitFraction(Fraction(997, 3), SEK), NOK.overdraft(1)),
            (SubunitFraction(Fraction(997, 3), SEK), 1),
        ),
    )
    def test_raises_type_error_for_invalid_other(
        self,
        a: SubunitFraction[Currency],
        b: object,
    ) -> None:
        with pytest.raises(
            TypeError,
            match=r"^unsupported operand type\(s\) for \-: 'SubunitFraction' and",
        ):
            a - b  # type: ignore[operator]
        with pytest.raises(
            TypeError,
            match=(
                r"^unsupported operand type\(s\) for \-: '(\w+)' and 'SubunitFraction'$"
            ),
        ):
            b - a  # type: ignore[operator]


class TestMul:
    @pytest.mark.parametrize(
        ("a", "b", "expected"),
        [
            (SEK.fraction(3, 4), 2, SEK.fraction(3, 2)),
            (SEK.fraction(3, 4), Fraction(1, 3), SEK.fraction(1, 4)),
        ],
    )
    def test_can_multiply(
        self,
        a: SubunitFraction[SEKType],
        b: int | Fraction,
        expected: SubunitFraction[SEKType],
    ) -> None:
        assert_type(a * b, SubunitFraction[SEKType])
        assert_type(b * a, SubunitFraction[SEKType])
        assert a * b == expected
        assert b * a == expected

    @pytest.mark.parametrize(
        ("a", "b"),
        (
            (
                SubunitFraction(Fraction(997, 3), SEK),
                SubunitFraction(Fraction(997, 3), SEK),
            ),
            (SubunitFraction(Fraction(997, 3), SEK), SEK(1)),
            (SubunitFraction(Fraction(997, 3), SEK), SEK.overdraft(1)),
            (SubunitFraction(Fraction(997, 3), SEK), object()),
        ),
    )
    def test_raises_type_error_for_invalid_other(
        self,
        a: SubunitFraction[Currency],
        b: object,
    ) -> None:
        with pytest.raises(
            TypeError,
            match=r"^unsupported operand type\(s\) for \*: 'SubunitFraction' and",
        ):
            a * b  # type: ignore[operator]
        with pytest.raises(
            TypeError,
            match=(
                r"^unsupported operand type\(s\) for \*: '(\w+)' and 'SubunitFraction'$"
            ),
        ):
            b * a  # type: ignore[operator]


class TestTruediv:
    @pytest.mark.parametrize(
        ("a", "b", "expected"),
        [
            (SEK.fraction(3, 4), 2, SEK.fraction(3, 8)),
            (SEK.fraction(3, 4), Fraction(1, 3), SEK.fraction(9, 4)),
        ],
    )
    def test_can_truediv(
        self,
        a: SubunitFraction[SEKType],
        b: int | Fraction,
        expected: SubunitFraction[SEKType],
    ) -> None:
        assert_type(a / b, SubunitFraction[SEKType])
        assert a / b == expected

    @pytest.mark.parametrize(
        ("a", "b", "expected"),
        [
            (2, SEK.fraction(3, 4), SEK.fraction(8, 3)),
            (Fraction(1, 3), SEK.fraction(3, 4), SEK.fraction(4, 9)),
        ],
    )
    def test_can_rtruediv(
        self,
        a: int | Fraction,
        b: SubunitFraction[SEKType],
        expected: SubunitFraction[SEKType],
    ) -> None:
        assert_type(a / b, SubunitFraction[SEKType])
        assert a / b == expected

    @pytest.mark.parametrize(
        ("a", "b"),
        (
            (SEK.fraction(997, 3), SEK(1)),
            (SEK.fraction(997, 3), SEK.overdraft(1)),
            (SEK.fraction(997, 3), object()),
            (SEK.fraction(997, 3), NOK.fraction(997, 3)),
        ),
    )
    def test_raises_type_error_for_invalid_other(
        self,
        a: SubunitFraction[Currency],
        b: object,
    ) -> None:
        with pytest.raises(
            TypeError,
            match=r"^unsupported operand type\(s\) for /: 'SubunitFraction' and",
        ):
            a / b  # type: ignore[operator]
        with pytest.raises(
            TypeError,
            match=(
                r"^unsupported operand type\(s\) for /: '(\w+)' and 'SubunitFraction'$"
            ),
        ):
            b / a  # type: ignore[operator]


class TestOrdering:
    @given(sek_monetaries, sek_monetaries)
    def test_total_ordering_within_currency(
        self, a: SEKMonetary, b: SEKMonetary
    ) -> None:
        assert (a > b and b < a) or (a < b and b > a) or (a == b and b == a)
        assert (a >= b and b <= a) or (a <= b and b >= a)

    @pytest.mark.parametrize(
        ("larger", "smaller"),
        [
            (SEK.fraction(0), SEK.overdraft_from_subunit(1)),
            (SEK.overdraft_from_subunit(1), SEK.fraction(-2)),
            (SEK.fraction(1), SEK.zero),
            (SEK.zero, SEK.fraction(-1)),
            (SEK(1), SEK.fraction(1, 2)),
        ],
    )
    def test_all_ordering_combinations(
        self,
        larger: SubunitFraction[Currency] | Overdraft[Currency] | Money[Currency],
        smaller: SubunitFraction[Currency] | Overdraft[Currency] | Money[Currency],
    ) -> None:
        assert larger > smaller
        assert not larger < smaller
        assert larger >= smaller
        assert not larger <= smaller
        assert smaller < larger
        assert not smaller > larger
        assert smaller <= larger
        assert not smaller >= larger

    @given(a=subunit_fractions(), b=overdrafts() | monies() | subunit_fractions())
    @example(NOK.fraction(1), SEK.fraction(1))
    @example(SEK.fraction(1), NOK.fraction(2))
    def test_raises_type_error_for_ordering_across_currencies(
        self,
        a: SubunitFraction[Currency],
        b: SubunitFraction[Currency] | Overdraft[Currency] | Money[Currency],
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
