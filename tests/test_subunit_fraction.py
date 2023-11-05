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

from .strategies import monies


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
