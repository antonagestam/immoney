from __future__ import annotations

from decimal import Decimal

from phantom import Phantom
from phantom.predicates.numeric import non_negative
from phantom.predicates.boolean import negate, all_of
import decimal


class PositiveDecimal(
    Decimal,
    Phantom[Decimal],
    predicate=all_of(
        (
        negate(Decimal.is_nan),
        Decimal.is_finite,
        non_negative,
        )
    ),
):
    @classmethod
    def parse(cls, instance: object) -> PositiveDecimal:
        if isinstance(instance, (str, int)):
            try:
                return super().parse(Decimal(instance))
            except decimal.InvalidOperation:
                pass
        return super().parse(instance)
