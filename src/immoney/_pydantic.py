from __future__ import annotations

import abc
from collections.abc import Iterable
from fractions import Fraction
from typing import Any
from typing import Protocol
from typing import TypedDict
from typing import TypeVar
from typing import get_args

from pydantic_core import core_schema
from pydantic_core.core_schema import GeneralValidatorFunction

from . import Currency
from . import Money
from . import Overdraft
from . import SubunitFraction
from .currencies import registry as default_registry
from .registry import CurrencyRegistry

C = TypeVar("C", bound=Currency)


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
        case invalid:  # pragma: no cover
            raise TypeError(f"Invalid type args: {invalid!r}.")


def or_is_instance(
    cls: type,
    wrapped: core_schema.CoreSchema,
    serialization: core_schema.SerSchema | None = None,
) -> core_schema.UnionSchema:
    return core_schema.union_schema(
        choices=[
            wrapped,
            core_schema.is_instance_schema(cls=cls),
        ],
        serialization=serialization,
    )


T_contra = TypeVar(
    "T_contra",
    Money[Currency],
    Overdraft[Currency],
    SubunitFraction[Currency],
    contravariant=True,
)
U_co = TypeVar("U_co", MoneyDict, OverdraftDict, SubunitFractionDict, covariant=True)


class GenericCurrencyAdapter(Protocol[T_contra, U_co]):
    @staticmethod
    @abc.abstractmethod
    def serialize(value: T_contra, *args: object) -> U_co:
        ...

    @staticmethod
    @abc.abstractmethod
    def schema(currency_schema: core_schema.CoreSchema) -> core_schema.CoreSchema:
        ...

    @staticmethod
    @abc.abstractmethod
    def validator_from_registry(
        registry: CurrencyRegistry[Currency],
    ) -> GeneralValidatorFunction:
        ...

    @staticmethod
    @abc.abstractmethod
    def validator_from_currency(currency: Currency) -> GeneralValidatorFunction:
        ...


class MoneyAdapter(GenericCurrencyAdapter[Money[Currency], MoneyDict]):
    @staticmethod
    def serialize(value: Money[Currency], *args: object) -> MoneyDict:
        return {
            "subunits": value.subunits,
            "currency": str(value.currency),
        }

    @staticmethod
    def schema(currency_schema: core_schema.CoreSchema) -> core_schema.CoreSchema:
        return or_is_instance(
            cls=Money,
            wrapped=core_schema.typed_dict_schema(
                {
                    "subunits": core_schema.typed_dict_field(
                        core_schema.int_schema(ge=0),
                        required=True,
                    ),
                    "currency": core_schema.typed_dict_field(
                        currency_schema,
                        required=True,
                    ),
                }
            ),
        )

    @staticmethod
    def validator_from_registry(
        registry: CurrencyRegistry[C],
    ) -> GeneralValidatorFunction:
        def validate_money(
            value: MoneyDict | Money[Currency],
            *args: object,
            _registry: CurrencyRegistry[C] = registry,
        ) -> Money[Currency]:
            if isinstance(value, Money):
                if value.currency.code not in _registry:
                    raise ValueError("Currency is not registered.")
                return value
            currency = _registry[value["currency"]]
            return currency.from_subunit(value["subunits"])

        return validate_money

    @staticmethod
    def validator_from_currency(currency: Currency) -> GeneralValidatorFunction:
        def validate_money(
            value: MoneyDict | Money[Currency],
            *args: object,
            _currency: Currency = currency,
        ) -> Money[Currency]:
            if isinstance(value, Money):
                if value.currency is not _currency:
                    raise ValueError(
                        f"Invalid currency, got {value.currency!r}, expected "
                        f"{_currency!r}."
                    )
                return value
            # We ignore coverage here as this is enforced by schema.
            if value["currency"] != _currency.code:  # pragma: no cover
                raise ValueError(f"Invalid currency, expected {_currency!s}.")
            return _currency.from_subunit(value["subunits"])

        return validate_money


class SubunitFractionAdapter(
    GenericCurrencyAdapter[SubunitFraction[Currency], SubunitFractionDict],
):
    @staticmethod
    def serialize(
        value: SubunitFraction[Currency],
        *args: object,
    ) -> SubunitFractionDict:
        return {
            "numerator": value.value.numerator,
            "denominator": value.value.denominator,
            "currency": str(value.currency),
        }

    @staticmethod
    def schema(currency_schema: core_schema.CoreSchema) -> core_schema.CoreSchema:
        return or_is_instance(
            cls=SubunitFraction,
            wrapped=core_schema.typed_dict_schema(
                {
                    "numerator": core_schema.typed_dict_field(
                        core_schema.int_schema(),
                        required=True,
                    ),
                    "denominator": core_schema.typed_dict_field(
                        core_schema.int_schema(),
                        required=True,
                    ),
                    "currency": core_schema.typed_dict_field(
                        currency_schema,
                        required=True,
                    ),
                }
            ),
        )

    @staticmethod
    def validator_from_registry(
        registry: CurrencyRegistry[C],
    ) -> GeneralValidatorFunction:
        def validate_subunit_fraction(
            value: SubunitFractionDict | SubunitFraction[Currency],
            *args: object,
            _registry: CurrencyRegistry[C] = registry,
        ) -> SubunitFraction[Currency]:
            if isinstance(value, SubunitFraction):
                if value.currency.code not in _registry:
                    raise ValueError("Currency is not registered.")
                return value
            currency = _registry[value["currency"]]
            fraction = Fraction(value["numerator"], value["denominator"])
            return currency.fraction(fraction)

        return validate_subunit_fraction

    @staticmethod
    def validator_from_currency(currency: Currency) -> GeneralValidatorFunction:
        def validate_subunit_fraction(
            value: SubunitFractionDict | SubunitFraction[Currency],
            *args: object,
            _currency: Currency = currency,
        ) -> SubunitFraction[Currency]:
            if isinstance(value, SubunitFraction):
                if value.currency is not _currency:
                    raise ValueError(
                        f"Invalid currency, got {value.currency!r}, expected "
                        f"{_currency!r}."
                    )
                return value
            # We ignore coverage here as this is enforced by schema.
            if value["currency"] != _currency.code:  # pragma: no cover
                raise ValueError(f"Invalid currency, expected {_currency!s}.")
            fraction = Fraction(value["numerator"], value["denominator"])
            return _currency.fraction(fraction)

        return validate_subunit_fraction


class OverdraftAdapter(GenericCurrencyAdapter[Overdraft[Currency], OverdraftDict]):
    @staticmethod
    def serialize(value: Overdraft[Currency], *args: object) -> OverdraftDict:
        return {
            "overdraft_subunits": value.subunits,
            "currency": str(value.currency),
        }

    @staticmethod
    def schema(currency_schema: core_schema.CoreSchema) -> core_schema.CoreSchema:
        return or_is_instance(
            cls=Overdraft,
            wrapped=core_schema.typed_dict_schema(
                {
                    "overdraft_subunits": core_schema.typed_dict_field(
                        core_schema.int_schema(gt=0),
                        required=True,
                    ),
                    "currency": core_schema.typed_dict_field(
                        currency_schema,
                        required=True,
                    ),
                }
            ),
        )

    @staticmethod
    def validator_from_registry(
        registry: CurrencyRegistry[C],
    ) -> GeneralValidatorFunction:
        def validate_overdraft(
            value: OverdraftDict | Overdraft[Currency],
            *args: object,
            _registry: CurrencyRegistry[C] = registry,
        ) -> Overdraft[Currency]:
            if isinstance(value, Overdraft):
                if value.currency.code not in _registry:
                    raise ValueError("Currency is not registered.")
                return value
            currency = _registry[value["currency"]]
            return currency.overdraft_from_subunit(value["overdraft_subunits"])

        return validate_overdraft

    @staticmethod
    def validator_from_currency(currency: Currency) -> GeneralValidatorFunction:
        def validate_overdraft(
            value: OverdraftDict | Overdraft[Currency],
            *args: object,
            _currency: Currency = currency,
        ) -> Overdraft[Currency]:
            if isinstance(value, Overdraft):
                if value.currency is not _currency:
                    raise ValueError(
                        f"Invalid currency, got {value.currency!r}, expected "
                        f"{_currency!r}."
                    )
                return value
            # We ignore coverage here as this is enforced by schema.
            if value["currency"] != _currency.code:  # pragma: no cover
                raise ValueError(f"Invalid currency, expected {_currency!s}.")
            return _currency.overdraft_from_subunit(value["overdraft_subunits"])

        return validate_overdraft


def currency_schema(currencies: Iterable[Currency]) -> core_schema.LiteralSchema:
    return core_schema.literal_schema([currency.code for currency in currencies])


def build_generic_currency_schema(
    cls: type,
    source_type: type,
    adapter: type[GenericCurrencyAdapter[Any, Any]],
) -> core_schema.CoreSchema:
    if source_type is cls:
        # Not specialized allow any default Currency.
        validator = adapter.validator_from_registry(default_registry)
        schema = adapter.schema(currency_schema(default_registry.values()))

    else:
        currency_type = extract_currency_type_arg(source_type)
        cls_registry = currency_type.get_default_registry()

        # Handle specialized to intermediate base class.
        if abc.ABC in currency_type.__bases__:
            validator = adapter.validator_from_registry(cls_registry)
            schema = adapter.schema(currency_schema(cls_registry.values()))

        # Handle specialized to a concrete currency class.
        else:
            currency = cls_registry[currency_type.code]
            validator = adapter.validator_from_currency(currency)
            schema = adapter.schema(currency_schema((currency,)))

    return core_schema.general_after_validator_function(
        schema=schema,
        function=validator,
        serialization=core_schema.wrap_serializer_function_ser_schema(
            function=adapter.serialize,
            schema=schema,
        ),
    )


def build_currency_schema(cls: type[C]) -> core_schema.CoreSchema:
    if abc.ABC not in cls.__bases__:
        raise NotImplementedError(
            "Using concrete Currency types as Pydantic fields is not yet supported."
        )

    cls_registry = cls.get_default_registry()

    def validate_currency(
        value: str,
        *args: object,
        registry: CurrencyRegistry[Currency] = cls_registry,
    ) -> Currency:
        if isinstance(value, str):
            return registry[value]
        # We ignore coverage here as this is enforced by schema.
        raise TypeError("Invalid type for Currency field.")  # pragma: no cover

    return or_is_instance(
        cls=cls,
        wrapped=core_schema.general_after_validator_function(
            function=validate_currency,
            schema=currency_schema(cls_registry.values()),
        ),
        serialization=core_schema.to_string_ser_schema(),
    )
