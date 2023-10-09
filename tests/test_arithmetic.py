import operator
from functools import reduce

from hypothesis import example
from hypothesis import given
from hypothesis.strategies import integers
from hypothesis.strategies import lists

from immoney import Money
from immoney import Overdraft
from immoney.currencies import SEK
from immoney.currencies import SEKType


def _to_integer_subunit(value: Money[SEKType] | Overdraft[SEKType]) -> int:
    return value.subunits if isinstance(value, Money) else -value.subunits


def _from_integer_subunit(value: int) -> Money[SEKType] | Overdraft[SEKType]:
    return SEK.from_subunit(value) if value >= 0 else SEK.overdraft_from_subunit(-value)


@given(lists(integers(), min_size=1))
@example([1])
@example([0, -1])
@example([10000000000000000000000000001])
def test_sequence_of_additions(values: list[int]):
    monetary_sum = sum((_from_integer_subunit(value) for value in values), SEK.zero)
    int_sum = sum(values)
    assert int_sum == _to_integer_subunit(monetary_sum)


@given(lists(integers(), min_size=1))
@example([1])
@example([0, -1])
@example([10000000000000000000000000001])
def test_sequence_of_subtractions(values: list[int]):
    monetary_delta = reduce(
        operator.sub,
        (_from_integer_subunit(value) for value in values),
    )
    int_delta = reduce(operator.sub, values)
    assert int_delta == _to_integer_subunit(monetary_delta)
