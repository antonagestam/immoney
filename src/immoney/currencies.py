from __future__ import annotations

from typing import Final, final

from . import Currency


@final
class SEKType(Currency):
    code = "SEK"
    subunit = 100


SEK: Final = SEKType()


@final
class NOKType(Currency):
    code = "SEK"
    subunit = 100


NOK: Final = NOKType()
