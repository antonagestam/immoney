from __future__ import annotations

from fractions import Fraction
from typing import Any
from typing import Final
from typing import TypedDict

from pydantic_core import core_schema

from . import Currency
from . import Money
from . import Overdraft
from . import SubunitFraction
from .currencies import registry
from .registry import CurrencyRegistry


class MoneyDict(TypedDict):
    subunits: int
    currency: str


class SubunitFractionDict(TypedDict):
    numerator: int
    denominator: int
    currency: str


class OverdraftDict(TypedDict):
    deficit_subunits: int
    currency: str


def currency_value_schema(registry: CurrencyRegistry) -> core_schema.LiteralSchema:
    return core_schema.literal_schema(*registry.keys())


def validate_currency(value: str | Currency, *args: object) -> Currency:
    return value if isinstance(value, Currency) else registry[value]


currency_schema: Final = core_schema.function_after_schema(
    function=validate_currency,
    schema=currency_value_schema(registry),
    serialization=core_schema.to_string_ser_schema(),
)


def validate_money(value: MoneyDict | Money[Any], *args: object) -> Money[Any]:
    if isinstance(value, Money):
        return value
    currency = registry[value["currency"]]
    return currency.from_subunit(value["subunits"])


def serialize_money(value: Money[Any], *args: object) -> MoneyDict:
    return {
        "subunits": value.as_subunit(),
        "currency": str(value.currency),
    }


money_dict: Final = core_schema.typed_dict_schema(
    {
        "subunits": core_schema.typed_dict_field(core_schema.int_schema(gt=0)),
        "currency": core_schema.typed_dict_field(currency_value_schema(registry)),
    }
)
money_schema: Final = core_schema.function_after_schema(
    schema=money_dict,
    function=validate_money,
    serialization=core_schema.function_wrap_ser_schema(
        function=serialize_money,
        schema=money_dict,
        json_return_type="dict",
    ),
)


def validate_subunit_fraction(
    value: SubunitFractionDict | SubunitFraction[Any],
    *args: object,
) -> SubunitFraction[Any]:
    if isinstance(value, SubunitFraction):
        return value
    currency = registry[value["currency"]]
    fraction = Fraction(value["numerator"], value["denominator"])
    return currency.fraction(fraction)


def serialize_subunit_fraction(
    value: SubunitFraction[Any],
    *args: object,
) -> SubunitFractionDict:
    return {
        "numerator": value.value.numerator,
        "denominator": value.value.denominator,
        "currency": str(value.currency),
    }


subunit_fraction_dict: Final = core_schema.typed_dict_schema(
    {
        "numerator": core_schema.typed_dict_field(core_schema.int_schema()),
        "denominator": core_schema.typed_dict_field(core_schema.int_schema()),
        "currency": core_schema.typed_dict_field(currency_value_schema(registry)),
    }
)
subunit_fraction_schema: Final = core_schema.function_after_schema(
    schema=subunit_fraction_dict,
    function=validate_subunit_fraction,
    serialization=core_schema.function_wrap_ser_schema(
        function=serialize_subunit_fraction,
        schema=subunit_fraction_dict,
        json_return_type="dict",
    ),
)


def validate_overdraft(
    value: OverdraftDict | Overdraft[Any],
    *args: object,
) -> Overdraft[Any]:
    if isinstance(value, Overdraft):
        return value
    currency = registry[value["currency"]]
    money_value = currency.from_subunit(value["deficit_subunits"])
    return Overdraft(money_value)


def serialize_overdraft(value: Overdraft[Any], *args: object) -> OverdraftDict:
    return {
        "deficit_subunits": value.money.as_subunit(),
        "currency": str(value.money.currency),
    }


overdraft_dict: Final = core_schema.typed_dict_schema(
    {
        "deficit_subunits": core_schema.typed_dict_field(core_schema.int_schema(gt=0)),
        "currency": core_schema.typed_dict_field(currency_value_schema(registry)),
    }
)
overdraft_schema: Final = core_schema.function_after_schema(
    schema=overdraft_dict,
    function=validate_overdraft,
    serialization=core_schema.function_wrap_ser_schema(
        function=serialize_overdraft,
        schema=overdraft_dict,
        json_return_type="dict",
    ),
)
