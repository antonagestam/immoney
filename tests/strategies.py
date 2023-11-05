from __future__ import annotations

import random
from typing import Final

from hypothesis.strategies import composite
from hypothesis.strategies import decimals
from hypothesis.strategies import integers
from hypothesis.strategies import text

from immoney import Currency
from immoney import Money
from immoney._base import Overdraft
from immoney._base import valid_subunit

valid_sek_decimals: Final = decimals(
    min_value=0,
    max_value=10_000_000_000_000_000_000_000_000 - 1,
    places=2,
    allow_nan=False,
    allow_infinity=False,
)

valid_money_subunits: Final = integers(min_value=0)
valid_overdraft_subunits: Final = integers(min_value=1)


@composite
def currencies(
    draw,
    code_values=text(max_size=3, min_size=3),
):
    class Subclass(Currency):
        subunit = random.choice(tuple(valid_subunit))
        code = draw(code_values)

    return Subclass()


@composite
def monies(
    draw,
    currencies=currencies(),
    subunits=integers(min_value=0),
) -> Money[Currency]:
    return Money.from_subunit(draw(subunits), draw(currencies))


@composite
def overdrafts(
    draw,
    currencies=currencies(),
    subunits=integers(min_value=1),
) -> Overdraft[Currency]:
    return Overdraft.from_subunit(draw(subunits), draw(currencies))
