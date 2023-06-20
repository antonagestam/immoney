from collections.abc import Mapping
from types import MappingProxyType
from typing import Generic
from typing import TypeAlias
from typing import TypeVar

from ._base import Currency

C = TypeVar("C", bound=Currency)
CurrencyRegistry: TypeAlias = Mapping[str, C]


class CurrencyCollector(Generic[C]):
    __slots__ = ("__collection",)

    def __init__(self) -> None:
        self.__collection = list[tuple[str, C]]()

    def add(self, currency: C) -> None:
        self.__collection.append((currency.code, currency))

    def finalize(self) -> CurrencyRegistry[C]:
        return MappingProxyType(dict(self.__collection))
