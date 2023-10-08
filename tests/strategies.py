from __future__ import annotations

from typing import Final

from hypothesis.strategies import decimals
from hypothesis.strategies import integers

valid_sek_decimals: Final = decimals(
    min_value=0,
    max_value=10_000_000_000_000_000_000_000_000 - 1,
    places=2,
    allow_nan=False,
    allow_infinity=False,
)

valid_money_subunits: Final = integers(min_value=0)
valid_overdraft_subunits: Final = integers(min_value=1)
