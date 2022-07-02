from __future__ import annotations

from typing import Final

from . import Currency


class SEKType(Currency):
    code = "SEK"
    subunit = 100


SEK: Final = SEKType()


class NOKType(Currency):
    code = "NOK"
    subunit = 100


NOK: Final = NOKType()


class EURType(Currency):
    code = "EUR"
    subunit = 100


EUR: Final = EURType()
