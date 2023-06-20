from __future__ import annotations

import abc
from typing import Final

from typing_extensions import assert_type

from immoney import Currency
from immoney.registry import CurrencyCollector
from immoney.registry import CurrencyRegistry


class CustomCurrency(Currency, abc.ABC):
    @classmethod
    def get_default_registry(cls) -> CurrencyRegistry[CustomCurrency]:
        return registry


__currencies: Final = CurrencyCollector[CustomCurrency]()


class JupiterCoinType(CustomCurrency):
    subunit = 100
    code = "JCN"


JCN: Final = JupiterCoinType()
__currencies.add(JCN)


class MoonCoinType(CustomCurrency):
    subunit = 1_000
    code = "MCN"


MCN: Final = MoonCoinType()
__currencies.add(MCN)


registry: Final = __currencies.finalize()
assert_type(registry, CurrencyRegistry[CustomCurrency])
del __currencies
