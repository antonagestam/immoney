from decimal import Decimal
from decimal import InvalidOperation
from typing import NewType

from .errors import ParseError

Nat = NewType("Nat", int)


def parse_nat(value: int) -> Nat:
    if value < 0:
        raise ParseError("Cannot parse from negative value")
    return Nat(value)


def approximate_decimal_subunits(
    main_unit: Decimal | str,
    subunit_per_main: int,
) -> Decimal:
    if isinstance(main_unit, str):
        try:
            main_unit = Decimal(main_unit)
        except InvalidOperation as exception:
            raise ParseError("Could not parse Money from the given str") from exception

    if main_unit.is_nan():
        raise ParseError("Cannot parse from NaN")
    if not main_unit.is_finite():
        raise ParseError("Cannot parse from non-finite")
    return main_unit * subunit_per_main
