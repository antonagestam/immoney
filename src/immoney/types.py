from __future__ import annotations

import decimal
from decimal import Decimal
from typing import TypeAlias

from phantom import Phantom
from phantom.predicates.boolean import all_of
from phantom.predicates.boolean import negate
from phantom.predicates.numeric import non_negative


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


ParsableMoneyValue: TypeAlias = int | str | Decimal
