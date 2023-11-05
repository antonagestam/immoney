import pytest

from immoney import Currency
from immoney import Money
from immoney import Overdraft
from immoney.babel import format_monetary
from immoney.currencies import KRW
from immoney.currencies import NOK
from immoney.currencies import SEK


@pytest.mark.parametrize(
    ("locale", "value", "expected_format"),
    [
        # Money values
        ("EN", KRW("1235"), "₩1,235"),
        ("NO", KRW("1235"), "KRW\xa01\xa0235"),
        ("KO", KRW("1235"), "₩1,235"),
        ("SW", KRW("1235"), "₩\xa01,235"),
        ("EN", NOK("12.35"), "NOK12.35"),
        ("NO", NOK("12.35"), "kr\xa012,35"),
        ("KO", NOK("12.35"), "NOK12.35"),
        ("SW", NOK("12.35"), "NOK\xa012.35"),
        ("EN", SEK("12.35"), "SEK12.35"),
        ("NO", SEK("12.35"), "SEK\xa012,35"),
        ("KO", SEK("12.35"), "SEK12.35"),
        ("SW", SEK("1235"), "SEK\xa01,235.00"),
        # Overdrafts
        ("EN", KRW.overdraft("1235"), "-₩1,235"),
        ("NO", KRW.overdraft("1235"), "KRW\xa0-1\xa0235"),
        ("KO", KRW.overdraft("1235"), "-₩1,235"),
        ("SW", KRW.overdraft("1235"), "-₩\xa01,235"),
        ("EN", NOK.overdraft("12.35"), "-NOK12.35"),
        ("NO", NOK.overdraft("12.35"), "kr\xa0-12,35"),
        ("KO", NOK.overdraft("12.35"), "-NOK12.35"),
        ("SW", NOK.overdraft("12.35"), "-NOK\xa012.35"),
        ("EN", SEK.overdraft("12.35"), "-SEK12.35"),
        ("NO", SEK.overdraft("12.35"), "SEK\xa0-12,35"),
        ("KO", SEK.overdraft("12.35"), "-SEK12.35"),
        ("SW", SEK.overdraft("1235"), "-SEK\xa01,235.00"),
    ],
)
def test_can_format_monetary(
    locale: str,
    value: Money[Currency] | Overdraft[Currency],
    expected_format: str,
) -> None:
    assert format_monetary(value, locale=locale) == expected_format
