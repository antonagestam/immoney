from __future__ import annotations

from fractions import Fraction
from typing import TypedDict
from typing import get_args

from pydantic_core import core_schema
from pydantic_core.core_schema import GeneralValidatorFunction
from pydantic_core.core_schema import TypedDictSchema

from . import Currency
from . import Money
from . import Overdraft
from . import SubunitFraction
from .registry import CurrencyRegistry


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


def extract_currency_type_arg(source_type: type) -> type[Currency]:
    match get_args(source_type):
        case (type() as currency_type,):
            assert issubclass(currency_type, Currency)
            return currency_type
        case invalid:
            raise TypeError(f"Invalid type args: {invalid!r}.")


def currency_value_schema(registry: CurrencyRegistry) -> core_schema.LiteralSchema:
    return core_schema.literal_schema(expected=list(registry.keys()))


def create_registry_money_validator(
    registry: CurrencyRegistry,
) -> GeneralValidatorFunction:
    def validate_money(
        value: MoneyDict | Money[Currency],
        *args: object,
        _registry: CurrencyRegistry = registry,
    ) -> Money[Currency]:
        if isinstance(value, Money):
            if value.currency.code not in _registry:
                raise ValueError("Currency not register.")
            return value
        currency = _registry[value["currency"]]
        return currency.from_subunit(value["subunits"])

    return validate_money


def create_concrete_money_validator(currency: Currency) -> GeneralValidatorFunction:
    def validate_money(
        value: MoneyDict | Money[Currency],
        *args: object,
        _currency: Currency = currency,
    ) -> Money[Currency]:
        if isinstance(value, Money):
            if value.currency is not _currency:
                raise ValueError(
                    f"Invalid currency, got {value.currency!r}, expected {_currency!r}."
                )
            return value
        if value["currency"] != _currency.code:
            raise ValueError(f"Invalid currency, expected {_currency!s}.")
        return _currency.from_subunit(value["subunits"])

    return validate_money


def serialize_money(value: Money[Currency], *args: object) -> MoneyDict:
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
    registry: CurrencyRegistry,
) -> GeneralValidatorFunction:
    def validate_subunit_fraction(
        value: SubunitFractionDict | SubunitFraction[Currency],
        *args: object,
        _registry: CurrencyRegistry = registry,
    ) -> SubunitFraction[Currency]:
        if isinstance(value, SubunitFraction):
            if value.currency.code not in _registry:
                raise ValueError("Currency is not registered.")
            return value
        currency = _registry[value["currency"]]
        fraction = Fraction(value["numerator"], value["denominator"])
        return currency.fraction(fraction)

    return validate_subunit_fraction


def create_concrete_fraction_validator(currency: Currency) -> GeneralValidatorFunction:
    def validate_subunit_fraction(
        value: SubunitFractionDict | SubunitFraction[Currency],
        *args: object,
        _currency: Currency = currency,
    ) -> SubunitFraction[Currency]:
        if isinstance(value, SubunitFraction):
            if value.currency is not _currency:
                raise ValueError(
                    f"Invalid currency, got {value.currency!r}, expected {_currency!r}."
                )
            return value
        if value["currency"] != _currency.code:
            raise ValueError(f"Invalid currency, expected {_currency!s}.")
        fraction = Fraction(value["numerator"], value["denominator"])
        return _currency.fraction(fraction)

    return validate_subunit_fraction


def serialize_subunit_fraction(
    value: SubunitFraction[Currency],
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


def create_registry_overdraft_validator(
    registry: CurrencyRegistry,
) -> GeneralValidatorFunction:
    def validate_overdraft(
        value: OverdraftDict | Overdraft[Currency],
        *args: object,
        _registry: CurrencyRegistry = registry,
    ) -> Overdraft[Currency]:
        if isinstance(value, Overdraft):
            if value.money.currency.code not in _registry:
                raise ValueError("Currency is not registered.")
            return value
        currency = _registry[value["currency"]]
        money_value = currency.from_subunit(value["overdraft_subunits"])
        return Overdraft(money_value)

    return validate_overdraft


def create_concrete_overdraft_validator(currency: Currency) -> GeneralValidatorFunction:
    def validate_overdraft(
        value: OverdraftDict | Overdraft[Currency],
        *args: object,
        _currency: Currency = currency,
    ) -> Overdraft[Currency]:
        if isinstance(value, Overdraft):
            if value.money.currency is not _currency:
                raise ValueError(
                    f"Invalid currency, got {value.money.currency!r}, expected "
                    f"{_currency!r}."
                )
            return value
        if value["currency"] != _currency.code:
            raise ValueError(f"Invalid currency, expected {_currency!s}.")
        money_value = _currency.from_subunit(value["overdraft_subunits"])
        return Overdraft(money_value)

    return validate_overdraft


def serialize_overdraft(value: Overdraft[Currency], *args: object) -> OverdraftDict:
    return {
        "overdraft_subunits": value.money.as_subunit(),
        "currency": str(value.money.currency),
    }


def create_registry_overdraft_dict(registry: CurrencyRegistry) -> TypedDictSchema:
    return core_schema.typed_dict_schema(
        {
            "overdraft_subunits": core_schema.typed_dict_field(
                core_schema.int_schema(gt=0)
            ),
            "currency": core_schema.typed_dict_field(currency_value_schema(registry)),
        }
    )


def create_concrete_overdraft_dict(currency: Currency) -> TypedDictSchema:
    return core_schema.typed_dict_schema(
        {
            "overdraft_subunits": core_schema.typed_dict_field(
                core_schema.int_schema(gt=0)
            ),
            "currency": core_schema.typed_dict_field(
                core_schema.literal_schema(expected=[currency.code])
            ),
        }
    )
