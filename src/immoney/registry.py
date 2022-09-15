from collections.abc import Mapping
from typing import TypeAlias

from immutables import Map

from ._base import Currency

CurrencyRegistry: TypeAlias = Mapping[str, Currency]


class CurrencyCollector:
    __slots__ = ("__collection",)

    def __init__(self) -> None:
        self.__collection = list[tuple[str, Currency]]()

    def add(self, currency: Currency) -> None:
        self.__collection.append((currency.code, currency))

    def finalize(self) -> CurrencyRegistry:
        return Map(self.__collection)
