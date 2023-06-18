from __future__ import annotations

from fractions import Fraction
from typing import Any
from typing import Final
from typing import TypedDict
from typing import get_args

from pydantic_core import core_schema
from pydantic_core.core_schema import TypedDictSchema

from . import Currency
from . import Money
from . import Overdraft
from . import SubunitFraction

# fixme: Should not depend on registry here, should always be parameterized.
from .currencies import registry
from .registry import CurrencyRegistry


def extract_currency_type_arg(source_type: type) -> type[Currency]:
    match get_args(source_type):
        case (type() as currency_type,):
            assert issubclass(currency_type, Currency)
            return currency_type
        case invalid:
            raise TypeError(f"Invalid type args: {invalid!r}.")


class MoneyDict(TypedDict):
    subunits: int
    currency: str


class SubunitFractionDict(TypedDict):
    numerator: int
    denominator: int
    currency: str


class OverdraftDict(TypedDict):
    overdraft_subunits: int
    currency: str


def currency_value_schema(registry: CurrencyRegistry) -> core_schema.LiteralSchema:
    # todo: Is list conversion really required here?
    return core_schema.literal_schema(expected=list(registry.keys()))


def create_registry_money_validator(
    default_registry: CurrencyRegistry,
) -> core_schema.GeneralValidatorFunction:
    def validate_money(
        value: MoneyDict | Money[Currency],
        *args: object,
        _registry: CurrencyRegistry = default_registry,
    ) -> Money[Currency]:
        if isinstance(value, Money):
            if value.currency.code not in _registry:
                raise ValueError("Currency not register.")
            return value
        currency = _registry[value["currency"]]
        return currency.from_subunit(value["subunits"])

    return validate_money


def create_concrete_money_validator(
    default_currency: Currency,
) -> core_schema.GeneralValidatorFunction:
    def validate_money(
        value: MoneyDict | Money[Currency],
        *args: object,
        currency: Currency = default_currency,
    ) -> Money[Currency]:
        if isinstance(value, Money):
            if value.currency is not currency:
                raise ValueError(
                    f"Invalid currency, got {value.currency!r}, expected {currency!r}."
                )
            return value
        if value["currency"] != currency.code:
            raise ValueError(f"Invalid currency, expected {currency!s}.")
        return currency.from_subunit(value["subunits"])

    return validate_money


def serialize_money(value: Money[Any], *args: object) -> MoneyDict:
    return {
        "subunits": value.as_subunit(),
        "currency": str(value.currency),
    }


def create_registry_money_dict(registry: CurrencyRegistry) -> TypedDictSchema:
    return core_schema.typed_dict_schema(
        {
            "subunits": core_schema.typed_dict_field(core_schema.int_schema(gt=0)),
            "currency": core_schema.typed_dict_field(currency_value_schema(registry)),
        }
    )


def create_concrete_money_dict(currency: Currency) -> TypedDictSchema:
    return core_schema.typed_dict_schema(
        {
            "subunits": core_schema.typed_dict_field(core_schema.int_schema(gt=0)),
            "currency": core_schema.typed_dict_field(
                core_schema.literal_schema(expected=[currency.code]),
            ),
        }
    )


def create_registry_fraction_validator(
    default_registry: CurrencyRegistry,
) -> core_schema.GeneralValidatorFunction:
    def validate_subunit_fraction(
        value: SubunitFractionDict | SubunitFraction[Currency],
        *args: object,
        _registry: CurrencyRegistry = default_registry,
    ) -> SubunitFraction[Currency]:
        if isinstance(value, SubunitFraction):
            if value.currency.code not in _registry:
                raise ValueError("Currency is not registered.")
            return value
        currency = _registry[value["currency"]]
        fraction = Fraction(value["numerator"], value["denominator"])
        return currency.fraction(fraction)

    return validate_subunit_fraction


def create_concrete_fraction_validator(
    default_currency: Currency,
) -> core_schema.GeneralValidatorFunction:
    def validate_subunit_fraction(
        value: SubunitFractionDict | SubunitFraction[Currency],
        *args: object,
        currency: Currency = default_currency,
    ) -> SubunitFraction[Currency]:
        if isinstance(value, SubunitFraction):
            if value.currency is not currency:
                raise ValueError(
                    f"Invalid currency, got {value.currency!r}, expected {currency!r}."
                )
            return value
        if value["currency"] != currency.code:
            raise ValueError(f"Invalid currency, expected {currency!s}.")
        fraction = Fraction(value["numerator"], value["denominator"])
        return currency.fraction(fraction)

    return validate_subunit_fraction


def serialize_subunit_fraction(
    value: SubunitFraction[Any],
    *args: object,
) -> SubunitFractionDict:
    return {
        "numerator": value.value.numerator,
        "denominator": value.value.denominator,
        "currency": str(value.currency),
    }


def create_registry_fraction_dict(registry: CurrencyRegistry) -> TypedDictSchema:
    return core_schema.typed_dict_schema(
        {
            "numerator": core_schema.typed_dict_field(core_schema.int_schema()),
            "denominator": core_schema.typed_dict_field(core_schema.int_schema()),
            "currency": core_schema.typed_dict_field(currency_value_schema(registry)),
        }
    )


def create_concrete_fraction_dict(currency: Currency) -> TypedDictSchema:
    return core_schema.typed_dict_schema(
        {
            "numerator": core_schema.typed_dict_field(core_schema.int_schema()),
            "denominator": core_schema.typed_dict_field(core_schema.int_schema()),
            "currency": core_schema.typed_dict_field(
                core_schema.literal_schema(expected=[currency.code]),
            ),
        }
    )


def validate_overdraft(
    value: OverdraftDict | Overdraft[Any],
    *args: object,
) -> Overdraft[Any]:
    if isinstance(value, Overdraft):
        return value
    currency = registry[value["currency"]]
    money_value = currency.from_subunit(value["overdraft_subunits"])
    return Overdraft(money_value)


def serialize_overdraft(value: Overdraft[Any], *args: object) -> OverdraftDict:
    return {
        "overdraft_subunits": value.money.as_subunit(),
        "currency": str(value.money.currency),
    }


overdraft_dict: Final = core_schema.typed_dict_schema(
    {
        "overdraft_subunits": core_schema.typed_dict_field(
            core_schema.int_schema(gt=0)
        ),
        "currency": core_schema.typed_dict_field(currency_value_schema(registry)),
    }
)
overdraft_schema: Final = core_schema.general_after_validator_function(
    schema=overdraft_dict,
    function=validate_overdraft,
    serialization=core_schema.wrap_serializer_function_ser_schema(
        function=serialize_overdraft,
        schema=overdraft_dict,
        # fixme
        # json_return_type="dict",
    ),
)
