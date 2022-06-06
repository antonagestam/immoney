from __future__ import annotations

from decimal import Decimal

from phantom import Phantom
from phantom.predicates.numeric import non_negative


class PositiveDecimal(Decimal, Phantom[Decimal], predicate=non_negative):
    @classmethod
    def parse(cls, instance: object) -> PositiveDecimal:
        return super().parse(
            Decimal(instance) if isinstance(instance, (str, int)) else instance
        )
