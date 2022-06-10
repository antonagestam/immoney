from __future__ import annotations

from decimal import Decimal
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
from immoney import Round
from immoney import SubunitFraction
from immoney.currencies import NOK
from immoney.currencies import SEK
from immoney.errors import FrozenInstanceError
from immoney.errors import MoneyParseError

valid_sek = decimals(
    min_value=0,
    max_value=100_000_000_000_000_000_000_000_000 - 1,
    places=2,
    allow_nan=False,
    allow_infinity=False,
)
valid_subunit_value = integers(min_value=1)
very_small_decimal = Decimal("0.0000000000000000000000000001")


@composite
def currencies(
    draw,
    subunit_values=integers(min_value=1, max_value=100_000_000_000),
    code_values=text(max_size=3, min_size=3),
):
    class Subclass(Currency):
        subunit = draw(subunit_values)
        code = draw(code_values)

    return Subclass()


class TestCurrency:
    def test_subclassing_with_missing_abstract_attribute_raises(self):
        with pytest.raises(UndefinedAbstractAttribute):
            type("sub", (Currency,), {"code": "foo"})

        with pytest.raises(UndefinedAbstractAttribute):
            type("sub", (Currency,), {"subunit": 1})

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

    @given(integers(min_value=1))
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
        next_plus = Money.from_subunit(instance.as_subunit() + 1, SEK)
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
