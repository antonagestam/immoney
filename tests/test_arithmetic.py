from __future__ import annotations

import enum
from collections.abc import Callable
from collections.abc import Sequence
from fractions import Fraction
from functools import reduce
from operator import add
from operator import mul
from operator import sub
from typing import Final
from typing import TypeAlias

from hypothesis import example
from hypothesis import given
from hypothesis.strategies import DrawFn
from hypothesis.strategies import SearchStrategy
from hypothesis.strategies import composite
from hypothesis.strategies import integers
from hypothesis.strategies import lists
from hypothesis.strategies import sampled_from

from immoney import Currency
from immoney import Money
from immoney import Overdraft
from immoney import SubunitFraction
from immoney.currencies import SEK
from immoney.currencies import SEKType


def _to_integer_subunit(value: Money[SEKType] | Overdraft[SEKType]) -> int:
    if isinstance(value, Money):
        return value.subunits
    elif isinstance(value, Overdraft):
        return -value.subunits
    raise NotImplementedError


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
        sub,
        (_from_integer_subunit(value) for value in values),
    )
    int_delta = reduce(sub, values)
    assert int_delta == _to_integer_subunit(monetary_delta)


def truediv(
    a: Numeric | Monetary,
    b: Numeric,
    /,
) -> Fraction | SubunitFraction[Currency]:
    if isinstance(a, int | Fraction):
        return Fraction(a, b)
    elif isinstance(a, Money | Overdraft | SubunitFraction):
        return a / b
    raise NotImplementedError


def rtruediv(
    a: Numeric | Monetary,
    b: Numeric,
    /,
) -> Fraction | SubunitFraction[Currency]:
    if isinstance(a, int | Fraction):
        return Fraction(b, a)
    elif isinstance(a, Money | Overdraft | SubunitFraction):
        return b / a
    raise NotImplementedError


def radd(
    a: Numeric | Monetary,
    b: Numeric,
    /,
) -> AnyVal:
    return add(b, a)  # type: ignore[no-any-return]


def rsub(
    a: Numeric | Monetary,
    b: Numeric,
    /,
) -> AnyVal:
    return sub(b, a)  # type: ignore[no-any-return]


def rmul(
    a: Numeric | Monetary,
    b: Numeric,
    /,
) -> AnyVal:
    return mul(b, a)  # type: ignore[no-any-return]


Numeric: TypeAlias = int | Fraction
Monetary: TypeAlias = Money[Currency] | Overdraft[Currency] | SubunitFraction[Currency]
AnyVal: TypeAlias = Numeric | Monetary

Operator: TypeAlias = (
    Callable[[Numeric, Numeric], Numeric]
    | Callable[[AnyVal, AnyVal], AnyVal]
    | Callable[[AnyVal, Numeric], Fraction | SubunitFraction[Currency]]
)
Operation: TypeAlias = tuple[Operator, Numeric]
MonetaryOperation: TypeAlias = tuple[Operator, AnyVal]
operators: Final = sub, add, mul, rmul, truediv, rtruediv


class SequenceError(enum.Enum):
    zero_division = enum.auto()


def to_subunit(value: Monetary) -> Numeric:
    if isinstance(value, Money):
        return value.subunits
    elif isinstance(value, Overdraft):
        return -value.subunits
    elif isinstance(value, SubunitFraction):
        return value.value
    raise NotImplementedError


def from_subunit(value: Numeric) -> Monetary:
    if isinstance(value, Fraction):
        return SubunitFraction(value, SEK)
    return _from_integer_subunit(value)


@composite
def operations(
    draw: DrawFn,
    operands: SearchStrategy[int] = integers(),
    ops: SearchStrategy[Operator] = sampled_from(operators),
) -> Operation:
    operator = draw(ops)
    operand = draw(operands)
    return operator, operand


def apply(value: AnyVal, operation: Operation | MonetaryOperation) -> AnyVal:
    operator, operand = operation
    return operator(value, operand)  # type: ignore[arg-type]


def monetary_operation(operation: Operation) -> MonetaryOperation:
    operator, operand = operation
    if operator in (sub, rsub, add, radd):
        return operator, from_subunit(operand)
    if operator in (mul, rmul, truediv, rtruediv):
        return operation
    raise NotImplementedError


@given(lists(operations()), integers())
@example(
    [
        (add, 16),
        (sub, 1),
        (radd, 18),
        (rsub, 64),
        (mul, 2),
        (rmul, 2),
        (truediv, 2),
        (truediv, 2),
        (rtruediv, 2),
    ],
    1,
)
# This found a bug where rtruediv returned 0 instead of raising a zero division error.
@example([(rtruediv, 0)], 0)
def test_sequence_of_operations(
    operations: Sequence[Operation],
    initial: int,
) -> None:
    monetary_result: int | Fraction | SequenceError
    int_result: int | Fraction | SequenceError

    try:
        monetary = reduce(
            apply,  # type: ignore[arg-type]
            (monetary_operation(operation) for operation in operations),
            from_subunit(initial),
        )
    except ZeroDivisionError:
        monetary_result = SequenceError.zero_division
    else:
        monetary_result = to_subunit(monetary)

    try:
        int_result = reduce(
            apply,  # type: ignore[arg-type]
            operations,
            initial,
        )
    except ZeroDivisionError:
        int_result = SequenceError.zero_division

    assert int_result == monetary_result
