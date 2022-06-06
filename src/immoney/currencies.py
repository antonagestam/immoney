from __future__ import annotations

from typing import Final
from typing import final

from . import Currency


@final
class SEKType(Currency):
    code = "SEK"
    subunit = 100


SEK: Final = SEKType()


@final
class NOKType(Currency):
    code = "NOK"
    subunit = 100


NOK: Final = NOKType()


@final
class EURType(Currency):
    code = "EUR"
    subunit = 100


EUR: Final = EURType()
