import json
from fractions import Fraction

import pytest
from pydantic import BaseModel
from pydantic import ValidationError
from typing_extensions import assert_type

from immoney import Currency
from immoney import Money
from immoney import Overdraft
from immoney import SubunitFraction
from immoney.currencies import CUP
from immoney.currencies import INR
from immoney.currencies import NOK
from immoney.currencies import USD
from immoney.currencies import CUPType
from immoney.currencies import INRType
from immoney.currencies import USDType

from .custom_currency import JCN
from .custom_currency import MCN
from .custom_currency import CustomCurrency


class DefaultCurrencyModel(BaseModel):
    currency: Currency


def test_can_roundtrip_default_currency_model() -> None:
    data = {"currency": "NOK"}

    instance = DefaultCurrencyModel.model_validate(data)

    assert_type(instance.currency, Currency)
    assert isinstance(instance, DefaultCurrencyModel)
    assert instance.currency is NOK
    assert json.loads(instance.model_dump_json()) == data


@pytest.mark.parametrize(
    ("value",),
    (
        ("",),
        ("boo",),
        ((),),
        (1,),
        ("JCN",),
        ("MCN",),
    ),
)
def test_can_refute_default_currency_model(value: object) -> None:
    with pytest.raises(
        ValidationError,
        match=r"Input should be.*\[type=literal_error",
    ):
        DefaultCurrencyModel.model_validate({"currency": value})


class CustomCurrencyModel(BaseModel):
    currency: CustomCurrency


@pytest.mark.parametrize(
    "currency",
    (MCN, JCN),
)
def test_can_roundtrip_custom_currency_model(
    currency: CustomCurrency,
) -> None:
    data = {"currency": currency.code}

    instance = CustomCurrencyModel.model_validate(data)

    assert_type(instance.currency, CustomCurrency)
    assert isinstance(instance, CustomCurrencyModel)
    assert instance.currency is currency
    assert json.loads(instance.model_dump_json()) == data


@pytest.mark.parametrize(
    ("value",),
    (
        ("",),
        ("boo",),
        ((),),
        (1,),
        ("SEK",),
        ("USD",),
    ),
)
def test_can_refute_custom_currency_model(value: object) -> None:
    with pytest.raises(
        ValidationError,
        match=r"Input should be.*\[type=literal_error",
    ):
        CustomCurrencyModel.model_validate({"currency": value})


def test_can_roundtrip_money_model() -> None:
    data = {
        "foo": {
            "subunits": 4990,
            "currency": "USD",
        }
    }

    class Model(BaseModel):
        # Important: do not specialize this type. The suppressed type error is expected.
        foo: Money  # type: ignore[type-arg]

    instance = Model.model_validate(data)
    assert instance.foo == USD("49.90")
    assert json.loads(instance.model_dump_json()) == data


class SpecializedMoneyModel(BaseModel):
    dollars: Money[USDType]


def test_can_roundtrip_specialized_money_model() -> None:
    data = {
        "dollars": {
            "subunits": 4990,
            "currency": "USD",
        }
    }

    instance = SpecializedMoneyModel.model_validate(data)
    assert instance.dollars == USD("49.90")
    assert json.loads(instance.model_dump_json()) == data
    assert_type(instance.dollars, Money[USDType])
    assert_type(instance.dollars.currency, USDType)


def test_can_refute_specialized_money_model() -> None:
    data = {
        "dollars": {
            "subunits": 4990,
            "currency": "SEK",
        }
    }

    with pytest.raises(ValidationError, match=r"Input should be 'USD'"):
        SpecializedMoneyModel.model_validate(data)


class CustomMoneyModel(BaseModel):
    coins: Money[CustomCurrency]


def test_can_roundtrip_custom_money_model() -> None:
    data = {
        "coins": {
            "subunits": 4990,
            "currency": "MCN",
        }
    }

    instance = CustomMoneyModel.model_validate(data)
    assert instance.coins == MCN.from_subunit(4990)
    assert json.loads(instance.model_dump_json()) == data
    assert_type(instance.coins, Money[CustomCurrency])
    assert_type(instance.coins.currency, CustomCurrency)


def test_can_refute_custom_money_model() -> None:
    data = {
        "coins": {
            "subunits": 4990,
            "currency": "SEK",
        }
    }

    with pytest.raises(
        ValidationError,
        match=r"Input should be '(MCN|JCN)' or '(MCN|JCN)'",
    ):
        CustomMoneyModel.model_validate(data)


class FractionModel(BaseModel):
    value_field: SubunitFraction  # type: ignore[type-arg]


@pytest.mark.parametrize(
    ("numerator", "denominator"),
    (
        (5, 3),
        (-5, 3),
        (-5, -3),
        (5, -3),
    ),
)
def test_can_roundtrip_subunit_fraction_model(numerator: int, denominator: int) -> None:
    expected = Fraction(numerator, denominator)
    data = {
        "value_field": {
            "numerator": numerator,
            "denominator": denominator,
            "currency": "INR",
        }
    }
    instance = FractionModel.model_validate(data)
    assert instance.value_field == INR.fraction(Fraction(numerator, denominator))
    assert json.loads(instance.model_dump_json()) == {
        "value_field": {
            "numerator": expected.numerator,
            "denominator": expected.denominator,
            "currency": "INR",
        }
    }


class CustomFractionModel(BaseModel):
    value_field: SubunitFraction[CustomCurrency]


def test_can_roundtrip_custom_subunit_fraction_model() -> None:
    expected = Fraction(5, 3)
    data = {
        "value_field": {
            "numerator": 5,
            "denominator": 3,
            "currency": "JCN",
        }
    }

    instance = CustomFractionModel.model_validate(data)

    assert instance.value_field == JCN.fraction(Fraction(5, 3))
    assert json.loads(instance.model_dump_json()) == {
        "value_field": {
            "numerator": expected.numerator,
            "denominator": expected.denominator,
            "currency": "JCN",
        }
    }
    assert_type(instance.value_field, SubunitFraction[CustomCurrency])
    assert_type(instance.value_field.currency, CustomCurrency)


def test_can_refute_custom_subunit_fraction_model() -> None:
    data = {
        "value_field": {
            "numerator": 5,
            "denominator": 3,
            "currency": "SEK",
        }
    }

    with pytest.raises(
        ValidationError,
        match=r"Input should be '(MCN|JCN)' or '(MCN|JCN)'",
    ):
        CustomFractionModel.model_validate(data)


class SpecializedFractionModel(BaseModel):
    value_field: SubunitFraction[INRType]


def test_can_roundtrip_specialized_subunit_fraction_model() -> None:
    expected = Fraction(13, 7)
    data = {
        "value_field": {
            "numerator": 13,
            "denominator": 7,
            "currency": "INR",
        }
    }

    instance = SpecializedFractionModel.model_validate(data)

    assert instance.value_field == INR.fraction(expected)
    assert json.loads(instance.model_dump_json()) == {
        "value_field": {
            "numerator": expected.numerator,
            "denominator": expected.denominator,
            "currency": "INR",
        }
    }
    assert_type(instance.value_field, SubunitFraction[INRType])
    assert_type(instance.value_field.currency, INRType)


def test_can_refute_specialized_subunit_fraction_model() -> None:
    data = {
        "value_field": {
            "numerator": 13,
            "denominator": 7,
            "currency": "USD",
        }
    }

    with pytest.raises(ValidationError, match=r"Input should be 'INR'"):
        SpecializedFractionModel.model_validate(data)


def test_can_roundtrip_overdraft_model() -> None:
    data = {
        "overdraft": {
            "overdraft_subunits": 89999,
            "currency": "CUP",
        }
    }

    class Model(BaseModel):
        overdraft: Overdraft  # type: ignore[type-arg]

    instance = Model.model_validate(data)
    assert instance.overdraft == CUP.overdraft("899.99")
    assert json.loads(instance.model_dump_json()) == data


class CustomOverdraftModel(BaseModel):
    overdraft: Overdraft[CustomCurrency]


def test_can_roundtrip_custom_overdraft_model() -> None:
    data = {
        "overdraft": {
            "overdraft_subunits": 89999,
            "currency": "MCN",
        }
    }

    instance = CustomOverdraftModel.model_validate(data)
    assert instance.overdraft == MCN.overdraft("89.999")
    assert json.loads(instance.model_dump_json()) == data
    assert_type(instance.overdraft, Overdraft[CustomCurrency])
    assert_type(instance.overdraft.money.currency, CustomCurrency)


def test_can_refute_custom_overdraft_model() -> None:
    data = {
        "overdraft": {
            "overdraft_subunits": 89999,
            "currency": "SEK",
        }
    }

    with pytest.raises(
        ValidationError,
        match=r"Input should be '(MCN|JCN)' or '(MCN|JCN)'",
    ):
        CustomOverdraftModel.model_validate(data)


class SpecializedOverdraftModel(BaseModel):
    overdraft: Overdraft[CUPType]


def test_can_roundtrip_specialized_overdraft_model() -> None:
    data = {
        "overdraft": {
            "overdraft_subunits": 89999,
            "currency": "CUP",
        }
    }

    instance = SpecializedOverdraftModel.model_validate(data)
    assert instance.overdraft == CUP.overdraft("899.99")
    assert json.loads(instance.model_dump_json()) == data
    assert_type(instance.overdraft, Overdraft[CUPType])
    assert_type(instance.overdraft.money.currency, CUPType)


def test_can_refute_specialized_overdraft_model() -> None:
    data = {
        "overdraft": {
            "overdraft_subunits": 89999,
            "currency": "EUR",
        }
    }

    with pytest.raises(ValidationError, match=r"Input should be 'CUP'"):
        SpecializedOverdraftModel.model_validate(data)
