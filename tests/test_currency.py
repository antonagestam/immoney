from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
from typing import Final

import pytest
from abcattrs import UndefinedAbstractAttribute
from hypothesis import example
from hypothesis import given
from hypothesis.strategies import decimals
from hypothesis.strategies import integers
from hypothesis.strategies import text

from immoney import Currency
from immoney import Money
from immoney import Overdraft
from immoney._base import SubunitFraction
from immoney._base import valid_subunit
from immoney.currencies import SEK
from immoney.errors import FrozenInstanceError
from immoney.errors import InvalidSubunit
from immoney.errors import ParseError

from .strategies import valid_money_subunits
from .strategies import valid_sek_decimals

very_small_decimal: Final = Decimal("0.0000000000000000000000000001")


def test_subclassing_with_missing_abstract_attribute_raises() -> None:
    with pytest.raises(UndefinedAbstractAttribute):
        type("sub", (Currency,), {"code": "foo"})

    with pytest.raises(UndefinedAbstractAttribute):
        type("sub", (Currency,), {"subunit": 1})


def test_subclassing_with_invalid_subunit_raises_value_error() -> None:
    with pytest.raises(InvalidSubunit):
        type("sub", (Currency,), {"subunit": 2, "code": "foo"})


@given(text())
def test_str_representation_is_code(test_code: str) -> None:
    class Subclass(Currency):
        code = test_code
        subunit = 1

    instance = Subclass()

    assert str(instance) == test_code


@given(valid_sek_decimals)
def test_call_instantiates_money(value: int) -> None:
    assert SEK(value) == Money(value, SEK)


@given(name=text(), value=valid_money_subunits | text())
@example(name="code", value="USD")
@example(name="subunit", value=1)
def test_raises_on_assignment(name: str, value: object) -> None:
    initial = getattr(SEK, name, None)

    with pytest.raises(FrozenInstanceError):
        setattr(SEK, name, value)

    assert SEK.code == "SEK"
    assert SEK.subunit == 100
    assert initial == getattr(SEK, name, None)


@pytest.mark.parametrize("subunit_value", valid_subunit)
def test_decimal_exponent_is_width_of_subunit(subunit_value: int) -> None:
    class Subclass(Currency):
        code = "foo"
        subunit = subunit_value

    instance = Subclass()

    assert instance.decimal_exponent == Decimal("0." + len(str(subunit_value)) * "0")


def test_zero_returns_cached_instance_of_money_zero() -> None:
    assert SEK.zero is SEK.zero
    assert SEK.zero.subunits == 0
    assert SEK.zero.currency is SEK


def test_normalize_value_raises_for_precision_loss() -> None:
    with pytest.raises(ParseError):
        SEK.normalize_to_subunits(Decimal("0.01") + very_small_decimal)


@given(
    value=integers(max_value=-1) | decimals(max_value=Decimal("-0.000001")),
)
def test_normalize_value_raises_for_negative_value(value: object) -> None:
    with pytest.raises(ParseError):
        SEK.normalize_to_subunits(value)


def test_normalize_value_raises_for_invalid_str() -> None:
    with pytest.raises(ParseError):
        SEK.normalize_to_subunits("foo")


def test_normalize_value_raises_for_nan() -> None:
    with pytest.raises(ParseError):
        SEK.normalize_to_subunits(Decimal("nan"))


def test_normalize_value_raises_for_non_finite() -> None:
    with pytest.raises(ParseError):
        SEK.normalize_to_subunits(Decimal("inf"))


def test_normalize_value_raises_for_invalid_type() -> None:
    with pytest.raises(NotImplementedError):
        SEK.normalize_to_subunits(float("inf"))


def test_from_subunit_returns_money_instance() -> None:
    instance = SEK.from_subunit(100)
    assert isinstance(instance, Money)
    assert instance.subunits == 100
    assert instance.decimal == Decimal("1.00")
    assert instance.currency is SEK


def test_overdraft_from_subunit_returns_overdraft_instance() -> None:
    instance = SEK.overdraft_from_subunit(100)
    assert isinstance(instance, Overdraft)
    assert instance.subunits == 100
    assert instance.decimal == Decimal("1.00")
    assert instance.currency is SEK


class TestFraction:
    def test_raises_type_error_for_incorrect_signature(self) -> None:
        with pytest.raises(
            TypeError, match=r"^Incorrect signature for Currency.fraction\(\)$"
        ):
            SEK.fraction(Fraction(1, 2), 1)  # type: ignore[call-overload]

    def test_can_construct_fraction_from_ints(self) -> None:
        value = SEK.fraction(2, 1)
        assert isinstance(value, SubunitFraction)
        assert value.value.numerator == 2
        assert value.value.denominator == 1
        assert value.currency is SEK

    @pytest.mark.parametrize(
        ("subunit_value", "expected_fraction"),
        (
            (1, Fraction(1)),
            (Decimal("1.5"), Fraction(3, 2)),
            (Fraction(11, 3), Fraction(11, 3)),
        ),
    )
    def test_can_construct_fraction_from_single_value(
        self,
        subunit_value: int | Decimal | Fraction,
        expected_fraction: Fraction,
    ) -> None:
        value = SEK.fraction(subunit_value)
        assert value.value == expected_fraction
        assert value.currency is SEK
