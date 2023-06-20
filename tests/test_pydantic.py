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
from immoney.currencies import CUP, NOKType, SEKType, SEK, EUR
from immoney.currencies import INR
from immoney.currencies import NOK
from immoney.currencies import USD
from immoney.currencies import CUPType
from immoney.currencies import INRType
from immoney.currencies import USDType
from immoney.currencies import registry as default_registry

from .check import sorted_items_equal
from .custom_currency import JCN
from .custom_currency import MCN
from .custom_currency import CustomCurrency


class DefaultCurrencyModel(BaseModel):
    currency: Currency


class TestDefaultCurrencyModel:
    def test_can_roundtrip_valid_data(self) -> None:
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
    def test_validation_raises_validation_error_for_invalid_values(self, value: object,) -> None:
        with pytest.raises(
            ValidationError,
            match=r"Input should be.*\[type=literal_error",
        ):
            DefaultCurrencyModel.model_validate({"currency": value})

    def test_can_instantiate_valid_value(self) -> None:
        instance = DefaultCurrencyModel(currency=USD)
        assert isinstance(instance, DefaultCurrencyModel)
        assert instance.currency is USD

    def test_instantiation_raises_validation_error_for_invalid_value(self) -> None:
        with pytest.raises(
            ValidationError,
            match=r"Input should be.*\[type=literal_error",
        ):
            DefaultCurrencyModel(currency=object())

    def test_can_generate_schema(self) -> None:
        assert DefaultCurrencyModel.model_json_schema() == {
            "properties": {
                "currency": {
                    "enum": sorted_items_equal(default_registry.keys()),
                    "title": "Currency",
                },
            },
            "required": ["currency"],
            "title": DefaultCurrencyModel.__name__,
            "type": "object",
        }


class CustomCurrencyModel(BaseModel):
    currency: CustomCurrency


class TestCustomCurrencyModel:
    @pytest.mark.parametrize(
        "currency",
        (MCN, JCN),
    )
    def test_can_roundtrip_valid_data(self, currency: CustomCurrency) -> None:
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
    def test_validation_raises_validation_error_for_invalid_values(self, value: object,) -> None:
        with pytest.raises(
            ValidationError,
            match=r"Input should be.*\[type=literal_error",
        ):
            CustomCurrencyModel.model_validate({"currency": value})

    def test_can_instantiate_valid_value(self) -> None:
        instance = CustomCurrencyModel(currency=JCN)
        assert isinstance(instance, CustomCurrencyModel)
        assert instance.currency is JCN

    def test_instantiation_raises_validation_error_for_invalid_value(self) -> None:
        with pytest.raises(
            ValidationError,
            match=r"Input should be.*\[type=literal_error",
        ):
            CustomCurrencyModel(currency=USD)

    def test_can_generate_schema(self) -> None:
        assert CustomCurrencyModel.model_json_schema() == {
            "properties": {
                "currency": {
                    "enum": sorted_items_equal(["MCN", "JCN"]),
                    "title": "Currency",
                },
            },
            "required": ["currency"],
            "title": CustomCurrencyModel.__name__,
            "type": "object",
        }


class MoneyModel(BaseModel):
    # Important: do not specialize this type. The suppressed type error is expected.
    money: Money  # type: ignore[type-arg]


class TestMoneyModel:
    def test_can_roundtrip_valid_data(self) -> None:
        data = {
            "money": {
                "subunits": 4990,
                "currency": "USD",
            }
        }

        instance = MoneyModel.model_validate(data)
        assert instance.money == USD("49.90")
        assert json.loads(instance.model_dump_json()) == data

    def test_parsing_raises_validation_error_for_invalid_currency(self) -> None:
        with pytest.raises(
            ValidationError,
            match=r"Input should be.*\[type=literal_error",
        ):
            MoneyModel.model_validate(
                {
                    "money": {"currency": "JCN", "subunits": 4990,},
                }
            )

    def test_can_instantiate_valid_value(self) -> None:
        instance = MoneyModel(money=USD("49.90"))
        assert instance.money == USD("49.90")

    def test_instantiation_raises_validation_error_for_invalid_currency(self) -> None:
        with pytest.raises(
            ValidationError,
            match=r"Currency not registered"
        ):
            MoneyModel(money=JCN(1))

    def test_can_generate_schema(self) -> None:
        assert MoneyModel.model_json_schema() == {
            "properties": {
                "money": {
                    "properties": {
                        "currency": {
                            "enum": sorted_items_equal(default_registry.keys()),
                            "title": "Currency",
                        },
                        "subunits": {
                            "exclusiveMinimum": 0,
                            "title": "Subunits",
                            "type": "integer",
                        },
                    },
                    "required": sorted_items_equal(["subunits", "currency"]),
                    "title": "Money",
                    "type": "object",
                },
            },
            "required": ["money"],
            "title": MoneyModel.__name__,
            "type": "object",
        }


class SpecializedMoneyModel(BaseModel):
    money: Money[USDType]


class TestSpecializedMoneyModel:
    def test_can_roundtrip_valid_data(self) -> None:
        data = {
            "money": {
                "subunits": 4990,
                "currency": "USD",
            }
        }

        instance = SpecializedMoneyModel.model_validate(data)
        assert instance.money == USD("49.90")
        assert json.loads(instance.model_dump_json()) == data
        assert_type(instance.money, Money[USDType])
        assert_type(instance.money.currency, USDType)

    def test_parsing_raises_validation_error_for_invalid_currency(self) -> None:
        data = {
            "money": {
                "subunits": 4990,
                "currency": "SEK",
            }
        }

        with pytest.raises(ValidationError, match=r"Input should be 'USD'"):
            SpecializedMoneyModel.model_validate(data)

    def test_can_instantiate_valid_value(self) -> None:
        instance = SpecializedMoneyModel(money=USD("49.90"))
        assert instance.money == USD("49.90")

    def test_instantiation_raises_validation_error_for_invalid_currency(self) -> None:
        with pytest.raises(
            ValidationError,
            match=r"Invalid currency"
        ):
            SpecializedMoneyModel(money=SEK(1))

    def test_can_generate_schema(self) -> None:
        assert SpecializedMoneyModel.model_json_schema() == {
            "properties": {
                "money": {
                    "properties": {
                        "currency": {
                            "const": "USD",
                            "title": "Currency",
                        },
                        "subunits": {
                            "exclusiveMinimum": 0,
                            "title": "Subunits",
                            "type": "integer",
                        },
                    },
                    "required": sorted_items_equal(["subunits", "currency"]),
                    "title": "Money",
                    "type": "object",
                },
            },
            "required": ["money"],
            "title": SpecializedMoneyModel.__name__,
            "type": "object",
        }


class CustomMoneyModel(BaseModel):
    money: Money[CustomCurrency]


class TestCustomMoneyModel:
    def test_can_roundtrip_valid_data(self) -> None:
        data = {
            "money": {
                "subunits": 4990,
                "currency": "MCN",
            }
        }

        instance = CustomMoneyModel.model_validate(data)
        assert instance.money == MCN.from_subunit(4990)
        assert json.loads(instance.model_dump_json()) == data
        assert_type(instance.money, Money[CustomCurrency])
        assert_type(instance.money.currency, CustomCurrency)

    def test_parsing_raises_validation_error_for_invalid_currency(self) -> None:
        data = {
            "money": {
                "subunits": 4990,
                "currency": "SEK",
            }
        }

        with pytest.raises(
            ValidationError,
            match=r"Input should be '(MCN|JCN)' or '(MCN|JCN)'",
        ):
            CustomMoneyModel.model_validate(data)

    def test_can_instantiate_valid_value(self) -> None:
        instance = CustomMoneyModel(money=MCN("49.90"))
        assert instance.money == MCN("49.90")

    def test_instantiation_raises_validation_error_for_invalid_currency(self) -> None:
        with pytest.raises(
            ValidationError,
            match=r"Currency not registered"
        ):
            CustomMoneyModel(money=USD(1))

    def test_can_generate_schema(self) -> None:
        assert CustomMoneyModel.model_json_schema() == {
            "properties": {
                "money": {
                    "properties": {
                        "currency": {
                            "enum": sorted_items_equal(("JCN", "MCN")),
                            "title": "Currency",
                        },
                        "subunits": {
                            "exclusiveMinimum": 0,
                            "title": "Subunits",
                            "type": "integer",
                        },
                    },
                    "required": sorted_items_equal(["subunits", "currency"]),
                    "title": "Money",
                    "type": "object",
                },
            },
            "required": ["money"],
            "title": CustomMoneyModel.__name__,
            "type": "object",
        }


class FractionModel(BaseModel):
    value_field: SubunitFraction  # type: ignore[type-arg]


class TestFractionModel:
    @pytest.mark.parametrize(
        ("numerator", "denominator"),
        (
            (5, 3),
            (-5, 3),
            (-5, -3),
            (5, -3),
        ),
    )
    def test_can_roundtrip_valid_data(self, numerator: int, denominator: int) -> None:
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

    def test_parsing_raises_validation_error_for_invalid_currency(self) -> None:
        with pytest.raises(
            ValidationError,
            match=r"Input should be.*\[type=literal_error",
        ):
            FractionModel.model_validate(
                {
                    "value_field": {
                        "currency": "JCN",
                        "numerator": 7,
                        "denominator": 5,
                    },
                }
            )

    def test_can_instantiate_valid_value(self) -> None:
        fraction = SEK.fraction(Fraction(13, 7))
        instance = FractionModel(value_field=fraction)
        assert instance.value_field is fraction

    def test_instantiation_raises_validation_error_for_invalid_currency(self) -> None:
        fraction = JCN.fraction(Fraction(13, 7))
        with pytest.raises(
            ValidationError,
            match=r"Currency is not registered"
        ):
            FractionModel(value_field=fraction)

    def test_can_generate_schema(self) -> None:
        assert FractionModel.model_json_schema() == {
            "properties": {
                "value_field": {
                    "properties": {
                        "currency": {
                            "enum": sorted_items_equal(default_registry.keys()),
                            "title": "Currency",
                        },
                        "numerator": {
                            "title": "Numerator",
                            "type": "integer",
                        },
                        "denominator": {
                            "title": "Denominator",
                            "type": "integer",
                        },
                    },
                    "required": sorted_items_equal(
                        ["currency", "numerator", "denominator"]
                    ),
                    "title": "Value Field",
                    "type": "object",
                },
            },
            "required": ["value_field"],
            "title": FractionModel.__name__,
            "type": "object",
        }


class CustomFractionModel(BaseModel):
    value_field: SubunitFraction[CustomCurrency]


class TestCustomFractionModel:
    def test_can_roundtrip_valid_data(self) -> None:
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

    def test_parsing_raises_validation_error_for_invalid_currency(self) -> None:
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

    def test_can_instantiate_valid_value(self) -> None:
        fraction = JCN.fraction(Fraction(13, 7))
        instance = CustomFractionModel(value_field=fraction)
        assert instance.value_field is fraction

    def test_instantiation_raises_validation_error_for_invalid_currency(self) -> None:
        fraction = SEK.fraction(Fraction(13, 7))
        with pytest.raises(
            ValidationError,
            match=r"Currency is not registered"
        ):
            CustomFractionModel(value_field=fraction)

    def test_can_generate_schema(self) -> None:
        assert CustomFractionModel.model_json_schema() == {
            "properties": {
                "value_field": {
                    "properties": {
                        "currency": {
                            "enum": sorted_items_equal(("MCN", "JCN")),
                            "title": "Currency",
                        },
                        "numerator": {
                            "title": "Numerator",
                            "type": "integer",
                        },
                        "denominator": {
                            "title": "Denominator",
                            "type": "integer",
                        },
                    },
                    "required": sorted_items_equal(
                        ["currency", "numerator", "denominator"]
                    ),
                    "title": "Value Field",
                    "type": "object",
                },
            },
            "required": ["value_field"],
            "title": CustomFractionModel.__name__,
            "type": "object",
        }


class SpecializedFractionModel(BaseModel):
    value_field: SubunitFraction[INRType]


class TestSpecializedFractionModel:
    def test_can_roundtrip_valid_data(self) -> None:
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

    def test_parsing_raises_validation_error_for_invalid_currency(self) -> None:
        data = {
            "value_field": {
                "numerator": 13,
                "denominator": 7,
                "currency": "USD",
            }
        }

        with pytest.raises(ValidationError, match=r"Input should be 'INR'"):
            SpecializedFractionModel.model_validate(data)

    def test_can_instantiate_valid_value(self) -> None:
        fraction = INR.fraction(Fraction(13, 7))
        instance = SpecializedFractionModel(value_field=fraction)
        assert instance.value_field is fraction

    def test_instantiation_raises_validation_error_for_invalid_currency(self) -> None:
        fraction = NOK.fraction(Fraction(13, 7))
        with pytest.raises(
            ValidationError,
            match=r"Invalid currency"
        ):
            SpecializedFractionModel(value_field=fraction)

    def test_can_generate_schema(self) -> None:
        assert SpecializedFractionModel.model_json_schema() == {
            "properties": {
                "value_field": {
                    "properties": {
                        "currency": {
                            "const": "INR",
                            "title": "Currency",
                        },
                        "numerator": {
                            "title": "Numerator",
                            "type": "integer",
                        },
                        "denominator": {
                            "title": "Denominator",
                            "type": "integer",
                        },
                    },
                    "required": sorted_items_equal(
                        ["currency", "numerator", "denominator"]
                    ),
                    "title": "Value Field",
                    "type": "object",
                },
            },
            "required": ["value_field"],
            "title": SpecializedFractionModel.__name__,
            "type": "object",
        }


class DefaultOverdraftModel(BaseModel):
    overdraft: Overdraft  # type: ignore[type-arg]


class TestDefaultOverdraftModel:
    def test_can_roundtrip_valid_data(self) -> None:
        data = {
            "overdraft": {
                "overdraft_subunits": 89999,
                "currency": "CUP",
            }
        }

        instance = DefaultOverdraftModel.model_validate(data)
        assert instance.overdraft == CUP.overdraft("899.99")
        assert json.loads(instance.model_dump_json()) == data

    def test_parsing_raises_validation_error_for_invalid_currency(self) -> None:
        with pytest.raises(
            ValidationError,
            match=r"Input should be.*\[type=literal_error",
        ):
            DefaultOverdraftModel.model_validate(
                {
                    "overdraft": {
                        "overdraft_subunits": 89999,
                        "currency": "MCN",
                    }
                }
            )

    def test_can_instantiate_valid_value(self) -> None:
        overdraft = SEK.overdraft("899.99")
        instance = DefaultOverdraftModel(overdraft=overdraft)
        assert instance.overdraft is overdraft

    def test_instantiation_raises_validation_error_for_invalid_currency(self) -> None:
        overdraft = JCN.overdraft("899.99")
        with pytest.raises(
            ValidationError,
            match=r"Currency is not registered"
        ):
            DefaultOverdraftModel(overdraft=overdraft)

    def test_can_generate_schema(self) -> None:
        assert DefaultOverdraftModel.model_json_schema() == {
            "properties": {
                "overdraft": {
                    "properties": {
                        "currency": {
                            "enum": sorted_items_equal(default_registry.keys()),
                            "title": "Currency",
                        },
                        "overdraft_subunits": {
                            "title": "Overdraft Subunits",
                            "type": "integer",
                            "exclusiveMinimum": 0,
                        },
                    },
                    "required": sorted_items_equal(["overdraft_subunits", "currency"]),
                    "title": "Overdraft",
                    "type": "object",
                },
            },
            "required": ["overdraft"],
            "title": DefaultOverdraftModel.__name__,
            "type": "object",
        }


class CustomOverdraftModel(BaseModel):
    overdraft: Overdraft[CustomCurrency]


class TestCustomOverdraftModel:
    def test_can_roundtrip_valid_data(self) -> None:
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

    def test_parsing_raises_validation_error_for_invalid_currency(self) -> None:
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

    def test_can_instantiate_valid_value(self) -> None:
        overdraft = JCN.overdraft("89.50")
        instance = CustomOverdraftModel(overdraft=overdraft)
        assert instance.overdraft is overdraft

    def test_instantiation_raises_validation_error_for_invalid_currency(self) -> None:
        overdraft = SEK.overdraft("89.50")
        with pytest.raises(
            ValidationError,
            match=r"Currency is not registered"
        ):
            CustomOverdraftModel(overdraft=overdraft)

    def test_can_generate_schema(self) -> None:
        assert CustomOverdraftModel.model_json_schema() == {
            "properties": {
                "overdraft": {
                    "properties": {
                        "currency": {
                            "enum": sorted_items_equal(["JCN", "MCN"]),
                            "title": "Currency",
                        },
                        "overdraft_subunits": {
                            "title": "Overdraft Subunits",
                            "type": "integer",
                            "exclusiveMinimum": 0,
                        },
                    },
                    "required": sorted_items_equal(["overdraft_subunits", "currency"]),
                    "title": "Overdraft",
                    "type": "object",
                },
            },
            "required": ["overdraft"],
            "title": CustomOverdraftModel.__name__,
            "type": "object",
        }


class SpecializedOverdraftModel(BaseModel):
    overdraft: Overdraft[CUPType]


class TestSpecializedOverdraftModel:
    def test_can_roundtrip_valid_data(self) -> None:
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

    def test_parsing_raises_validation_error_for_invalid_currency(self) -> None:
        data = {
            "overdraft": {
                "overdraft_subunits": 89999,
                "currency": "EUR",
            }
        }

        with pytest.raises(ValidationError, match=r"Input should be 'CUP'"):
            SpecializedOverdraftModel.model_validate(data)

    def test_can_instantiate_valid_value(self) -> None:
        overdraft = CUP.overdraft(90)
        instance = SpecializedOverdraftModel(overdraft=overdraft)
        assert instance.overdraft is overdraft

    def test_instantiation_raises_validation_error_for_invalid_currency(self) -> None:
        overdraft = EUR.overdraft(99)
        with pytest.raises(
            ValidationError,
            match=r"Invalid currency"
        ):
            SpecializedOverdraftModel(overdraft=overdraft)

    def test_can_generate_schema(self) -> None:
        assert SpecializedOverdraftModel.model_json_schema() == {
            "properties": {
                "overdraft": {
                    "properties": {
                        "currency": {
                            "const": "CUP",
                            "title": "Currency",
                        },
                        "overdraft_subunits": {
                            "title": "Overdraft Subunits",
                            "type": "integer",
                            "exclusiveMinimum": 0,
                        },
                    },
                    "required": sorted_items_equal(["overdraft_subunits", "currency"]),
                    "title": "Overdraft",
                    "type": "object",
                },
            },
            "required": ["overdraft"],
            "title": SpecializedOverdraftModel.__name__,
            "type": "object",
        }
