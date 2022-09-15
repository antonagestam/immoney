from typing import Final
from typing import final

import pytest

from immoney import Currency
from immoney import currencies
from immoney.registry import CurrencyCollector

collector: Final = CurrencyCollector()


@final
class SEKType(Currency):
    code = "SEK"
    subunit = 100


SEK: Final = SEKType()
collector.add(SEK)


@final
class ZWNType(Currency):
    code = "ZWN"
    subunit = 100


ZWN: Final = ZWNType()
collector.add(ZWN)


@final
class XYZType(Currency):
    code = "XYZ"
    subunit = 100


XYZ: Final = XYZType()
collector.add(XYZ)


custom_registry: Final = collector.finalize()


class TestCustomRegistry:
    @pytest.mark.parametrize(
        ("name", "expected_instance"),
        [
            ("SEK", SEK),
            ("ZWN", ZWN),
            ("XYZ", XYZ),
        ],
    )
    def test_can_get_currency(self, name: str, expected_instance: Currency):
        assert custom_registry[name] is expected_instance

    def test_raises_key_error_for_missing_currency(self):
        with pytest.raises(KeyError):
            custom_registry["USD"]


class TestDefaultRegistry:
    @pytest.mark.parametrize(
        ("name", "expected_instance"),
        [
            ("SEK", currencies.SEK),
            ("ZWN", currencies.ZWN),
            ("USD", currencies.USD),
            ("JPY", currencies.JPY),
        ],
    )
    def test_can_get_currency(self, name: str, expected_instance: Currency):
        assert currencies.registry[name] is expected_instance

    def test_raises_key_error_for_missing_currency(self):
        with pytest.raises(KeyError):
            currencies.registry["_sek"]
