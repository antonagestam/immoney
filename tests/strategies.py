from __future__ import annotations

from typing import Final

from hypothesis.strategies import decimals

max_valid_sek: Final = 10_000_000_000_000_000_000_000_000 - 1
valid_sek: Final = decimals(
    min_value=0,
    max_value=max_valid_sek,
    places=2,
    allow_nan=False,
    allow_infinity=False,
)
