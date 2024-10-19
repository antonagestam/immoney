import json
from fractions import Fraction
from typing import Generic
from typing import TypeVar

import pytest
from pydantic import BaseModel
from pydantic import ValidationError
from typing_extensions import assert_type

from immoney import Currency
from immoney import Money
from immoney import Overdraft
from immoney import SubunitFraction
from immoney.currencies import CUP
from immoney.currencies import EUR
from immoney.currencies import INR
from immoney.currencies import NOK
from immoney.currencies import SEK
from immoney.currencies import USD
from immoney.currencies import CUPType
from immoney.currencies import INRType
from immoney.currencies import USDType
from immoney.currencies import registry as default_registry

from .check import sorted_items_equal
from .custom_currency import JCN
from .custom_currency import MCN
from .custom_currency import CustomCurrency


def test_cannot_use_concrete_currency_as_field_type() -> None:
    with pytest.raises(
        NotImplementedError,
        match=(
            r"^Using concrete Currency types as Pydantic fields is not yet supported"
        ),
    ):

        class SpecializedCurrencyModel(BaseModel):
            currency: INRType


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
    def test_validation_raises_validation_error_for_invalid_values(
        self,
        value: object,
    ) -> None:
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
            DefaultCurrencyModel(currency=object())  # type: ignore[arg-type]

    def test_can_generate_schema(self) -> None:
        assert DefaultCurrencyModel.model_json_schema() == {
            "properties": {
                "currency": {
                    "enum": sorted_items_equal(default_registry.keys()),
                    "title": "Currency",
                    "type": "string",
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
    def test_validation_raises_validation_error_for_invalid_values(
        self,
        value: object,
    ) -> None:
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
            CustomCurrencyModel(currency=USD)  # type: ignore[arg-type]

    def test_can_generate_schema(self) -> None:
        assert CustomCurrencyModel.model_json_schema() == {
            "properties": {
                "currency": {
                    "enum": sorted_items_equal(["MCN", "JCN"]),
                    "title": "Currency",
                    "type": "string",
                },
            },
            "required": ["currency"],
            "title": CustomCurrencyModel.__name__,
            "type": "object",
        }


class MoneyModel(BaseModel):
    # Important: do not specialize this type.
    money: Money


class TestMoneyModel:
    @pytest.mark.parametrize(
        ("subunits", "currency_code", "expected"),
        (
            (4990, "USD", USD("49.90")),
            (4990, "EUR", EUR("49.90")),
            (0, "NOK", NOK(0)),
        ),
    )
    def test_can_roundtrip_valid_data(
        self,
        subunits: int,
        currency_code: str,
        expected: Money[Currency],
    ) -> None:
        data = {
            "money": {
                "subunits": subunits,
                "currency": currency_code,
            }
        }

        instance = MoneyModel.model_validate(data)
        assert_type(instance.money, Money[Currency])
        assert instance.money == expected
        assert json.loads(instance.model_dump_json()) == data

    def test_parsing_raises_validation_error_for_negative_value(self) -> None:
        with pytest.raises(
            ValidationError,
            match=r"Input should be greater than or equal to 0",
        ):
            MoneyModel.model_validate(
                {
                    "money": {
                        "currency": "EUR",
                        "subunits": -1,
                    },
                }
            )

    def test_parsing_raises_validation_error_for_invalid_currency(self) -> None:
        with pytest.raises(
            ValidationError,
            match=r"Input should be.*\[type=literal_error",
        ):
            MoneyModel.model_validate(
                {
                    "money": {
                        "currency": "JCN",
                        "subunits": 4990,
                    },
                }
            )

    def test_can_instantiate_valid_value(self) -> None:
        instance = MoneyModel(money=USD("49.90"))
        assert instance.money == USD("49.90")

    def test_instantiation_raises_validation_error_for_invalid_currency(self) -> None:
        with pytest.raises(ValidationError, match=r"Currency is not registered"):
            MoneyModel(money=JCN(1))

    def test_can_generate_schema(self) -> None:
        assert MoneyModel.model_json_schema() == {
            "properties": {
                "money": {
                    "properties": {
                        "currency": {
                            "enum": sorted_items_equal(default_registry.keys()),
                            "title": "Currency",
                            "type": "string",
                        },
                        "subunits": {
                            "minimum": 0,
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


C_bounded = TypeVar("C_bounded", bound=Currency)


class BoundedGenericMoneyModel(BaseModel, Generic[C_bounded]):
    money: Money[C_bounded]


class TestBoundedGenericMoneyModel:
    @pytest.mark.parametrize(
        ("subunits", "currency_code", "expected"),
        (
            (4990, "USD", USD("49.90")),
            (4990, "EUR", EUR("49.90")),
            (0, "NOK", NOK(0)),
        ),
    )
    def test_can_roundtrip_valid_data(
        self,
        subunits: int,
        currency_code: str,
        expected: Money[C_bounded],
    ) -> None:
        data = {
            "money": {
                "subunits": subunits,
                "currency": currency_code,
            }
        }

        instance = BoundedGenericMoneyModel[C_bounded].model_validate(data)
        assert instance.money == expected
        assert json.loads(instance.model_dump_json()) == data

    def test_parsing_raises_validation_error_for_negative_value(self) -> None:
        with pytest.raises(
            ValidationError,
            match=r"Input should be greater than or equal to 0",
        ):
            BoundedGenericMoneyModel.model_validate(
                {
                    "money": {
                        "currency": "EUR",
                        "subunits": -1,
                    },
                }
            )

    def test_parsing_raises_validation_error_for_invalid_currency(self) -> None:
        with pytest.raises(
            ValidationError,
            match=r"Input should be.*\[type=literal_error",
        ):
            BoundedGenericMoneyModel.model_validate(
                {
                    "money": {
                        "currency": "JCN",
                        "subunits": 4990,
                    },
                }
            )

    def test_can_instantiate_valid_value(self) -> None:
        instance = BoundedGenericMoneyModel(money=USD("49.90"))
        assert instance.money == USD("49.90")

    def test_instantiation_raises_validation_error_for_invalid_currency(self) -> None:
        with pytest.raises(ValidationError, match=r"Currency is not registered"):
            BoundedGenericMoneyModel(money=JCN(1))

    def test_can_generate_schema(self) -> None:
        assert BoundedGenericMoneyModel.model_json_schema() == {
            "properties": {
                "money": {
                    "properties": {
                        "currency": {
                            "enum": sorted_items_equal(default_registry.keys()),
                            "title": "Currency",
                            "type": "string",
                        },
                        "subunits": {
                            "minimum": 0,
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
            "title": BoundedGenericMoneyModel.__name__,
            "type": "object",
        }


C_unbound = TypeVar("C_unbound")


class UnboundGenericMoneyModel(BaseModel, Generic[C_unbound]):
    # mypy rightfully errors here, demanding that the type var is bounded to
    # Currency, but we still want to test this case.
    money: Money[C_unbound]  # type: ignore[type-var]


class TestUnboundGenericMoneyModel:
    @pytest.mark.parametrize(
        ("subunits", "currency_code", "expected"),
        (
            (4990, "USD", USD("49.90")),
            (4990, "EUR", EUR("49.90")),
            (0, "NOK", NOK(0)),
        ),
    )
    def test_can_roundtrip_valid_data(
        self,
        subunits: int,
        currency_code: str,
        expected: Money[C_unbound],  # type: ignore[type-var]
    ) -> None:
        data = {
            "money": {
                "subunits": subunits,
                "currency": currency_code,
            }
        }

        instance = UnboundGenericMoneyModel[C_unbound].model_validate(data)
        assert instance.money == expected
        assert json.loads(instance.model_dump_json()) == data

    def test_parsing_raises_validation_error_for_negative_value(self) -> None:
        with pytest.raises(
            ValidationError,
            match=r"Input should be greater than or equal to 0",
        ):
            UnboundGenericMoneyModel.model_validate(
                {
                    "money": {
                        "currency": "EUR",
                        "subunits": -1,
                    },
                }
            )

    def test_parsing_raises_validation_error_for_invalid_currency(self) -> None:
        with pytest.raises(
            ValidationError,
            match=r"Input should be.*\[type=literal_error",
        ):
            UnboundGenericMoneyModel.model_validate(
                {
                    "money": {
                        "currency": "JCN",
                        "subunits": 4990,
                    },
                }
            )

    def test_can_instantiate_valid_value(self) -> None:
        instance = UnboundGenericMoneyModel(money=USD("49.90"))
        assert instance.money == USD("49.90")

    def test_instantiation_raises_validation_error_for_invalid_currency(self) -> None:
        with pytest.raises(ValidationError, match=r"Currency is not registered"):
            UnboundGenericMoneyModel(money=JCN(1))

    def test_can_generate_schema(self) -> None:
        assert UnboundGenericMoneyModel.model_json_schema() == {
            "properties": {
                "money": {
                    "properties": {
                        "currency": {
                            "enum": sorted_items_equal(default_registry.keys()),
                            "title": "Currency",
                            "type": "string",
                        },
                        "subunits": {
                            "minimum": 0,
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
            "title": UnboundGenericMoneyModel.__name__,
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
        with pytest.raises(ValidationError, match=r"Invalid currency"):
            SpecializedMoneyModel(money=SEK(1))  # type: ignore[arg-type]

    def test_can_generate_schema(self) -> None:
        assert SpecializedMoneyModel.model_json_schema() == {
            "properties": {
                "money": {
                    "properties": {
                        "currency": {
                            "const": "USD",
                            "title": "Currency",
                            "enum": ["USD"],
                            "type": "string",
                        },
                        "subunits": {
                            "minimum": 0,
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
        with pytest.raises(ValidationError, match=r"Currency is not registered"):
            CustomMoneyModel(money=USD(1))  # type: ignore[arg-type]

    def test_can_generate_schema(self) -> None:
        assert CustomMoneyModel.model_json_schema() == {
            "properties": {
                "money": {
                    "properties": {
                        "currency": {
                            "enum": sorted_items_equal(("JCN", "MCN")),
                            "title": "Currency",
                            "type": "string",
                        },
                        "subunits": {
                            "minimum": 0,
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
    value_field: SubunitFraction


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
        assert_type(instance.value_field, SubunitFraction[Currency])
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
        with pytest.raises(ValidationError, match=r"Currency is not registered"):
            FractionModel(value_field=fraction)

    def test_can_generate_schema(self) -> None:
        assert FractionModel.model_json_schema() == {
            "properties": {
                "value_field": {
                    "properties": {
                        "currency": {
                            "enum": sorted_items_equal(default_registry.keys()),
                            "title": "Currency",
                            "type": "string",
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
        with pytest.raises(ValidationError, match=r"Currency is not registered"):
            CustomFractionModel(value_field=fraction)  # type: ignore[arg-type]

    def test_can_generate_schema(self) -> None:
        assert CustomFractionModel.model_json_schema() == {
            "properties": {
                "value_field": {
                    "properties": {
                        "currency": {
                            "enum": sorted_items_equal(("MCN", "JCN")),
                            "title": "Currency",
                            "type": "string",
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
        with pytest.raises(ValidationError, match=r"Invalid currency"):
            SpecializedFractionModel(value_field=fraction)  # type: ignore[arg-type]

    def test_can_generate_schema(self) -> None:
        assert SpecializedFractionModel.model_json_schema() == {
            "properties": {
                "value_field": {
                    "properties": {
                        "currency": {
                            "const": "INR",
                            "title": "Currency",
                            "enum": ["INR"],
                            "type": "string",
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
    overdraft: Overdraft


class TestDefaultOverdraftModel:
    @pytest.mark.parametrize(
        ("subunits", "currency_code", "expected"),
        (
            (4990, "USD", USD.overdraft("49.90")),
            (4990, "EUR", EUR.overdraft("49.90")),
            (1, "NOK", NOK.overdraft("0.01")),
        ),
    )
    def test_can_roundtrip_valid_data(
        self,
        subunits: int,
        currency_code: str,
        expected: Overdraft[Currency],
    ) -> None:
        data = {
            "overdraft": {
                "overdraft_subunits": subunits,
                "currency": currency_code,
            }
        }

        instance = DefaultOverdraftModel.model_validate(data)
        assert_type(instance.overdraft, Overdraft[Currency])
        assert instance.overdraft == expected
        assert json.loads(instance.model_dump_json()) == data

    @pytest.mark.parametrize("value", (0, -1, -1024))
    def test_parsing_raises_validation_error_for_non_positive_value(
        self,
        value: int,
    ) -> None:
        with pytest.raises(
            ValidationError,
            match=r"Input should be greater than 0",
        ):
            DefaultOverdraftModel.model_validate(
                {
                    "overdraft": {
                        "currency": "EUR",
                        "overdraft_subunits": value,
                    },
                }
            )

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
        with pytest.raises(ValidationError, match=r"Currency is not registered"):
            DefaultOverdraftModel(overdraft=overdraft)

    def test_can_generate_schema(self) -> None:
        assert DefaultOverdraftModel.model_json_schema() == {
            "properties": {
                "overdraft": {
                    "properties": {
                        "currency": {
                            "enum": sorted_items_equal(default_registry.keys()),
                            "title": "Currency",
                            "type": "string",
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
        assert_type(instance.overdraft.currency, CustomCurrency)

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
        with pytest.raises(ValidationError, match=r"Currency is not registered"):
            CustomOverdraftModel(overdraft=overdraft)  # type: ignore[arg-type]

    def test_can_generate_schema(self) -> None:
        assert CustomOverdraftModel.model_json_schema() == {
            "properties": {
                "overdraft": {
                    "properties": {
                        "currency": {
                            "enum": sorted_items_equal(["JCN", "MCN"]),
                            "title": "Currency",
                            "type": "string",
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
        assert_type(instance.overdraft.currency, CUPType)

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
        with pytest.raises(ValidationError, match=r"Invalid currency"):
            SpecializedOverdraftModel(overdraft=overdraft)  # type: ignore[arg-type]

    def test_can_generate_schema(self) -> None:
        assert SpecializedOverdraftModel.model_json_schema() == {
            "properties": {
                "overdraft": {
                    "properties": {
                        "currency": {
                            "const": "CUP",
                            "title": "Currency",
                            "enum": ["CUP"],
                            "type": "string",
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
