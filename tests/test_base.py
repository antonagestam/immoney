from decimal import Decimal

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
from immoney.currencies import SEK
from immoney.errors import MoneyParseError

valid_sek = decimals(min_value=0, places=2, allow_nan=False, allow_infinity=False)
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
        with pytest.raises(AttributeError):
            setattr(SEK, name, value)

        assert SEK.__dict__ == {}
        assert SEK.code == "SEK"
        assert SEK.subunit == 100

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
            # breakpoint()

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
