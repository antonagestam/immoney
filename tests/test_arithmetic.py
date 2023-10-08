from hypothesis import given
from hypothesis.strategies import integers
from hypothesis.strategies import lists
from typing_extensions import assert_type

from immoney import Money
from immoney import Overdraft
from immoney.currencies import SEK
from immoney.currencies import SEKType

from .strategies import max_valid_sek


def _to_integer_subunit(value: Money[SEKType] | Overdraft[SEKType]) -> int:
    return value.subunits if isinstance(value, Money) else -value.subunits


def _from_integer_subunit(value: int) -> Money[SEKType] | Overdraft[SEKType]:
    return SEK.from_subunit(value) if value >= 0 else SEK.overdraft_from_subunit(-value)


@given(lists(integers(max_value=max_valid_sek, min_value=-max_valid_sek), min_size=1))
def test_arithmetics(values: list[int]):
    monetary_sum: Money[SEKType] | Overdraft[SEKType] = sum(
        (_from_integer_subunit(value) for value in values),
        SEK(0),
    )
    assert_type(
        monetary_sum,
        Money[SEKType] | Overdraft[SEKType],
    )
    int_sum = sum(values)
    assert int_sum == _to_integer_subunit(monetary_sum)
