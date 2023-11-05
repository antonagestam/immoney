from collections.abc import Callable
from decimal import Decimal
from typing import Concatenate
from typing import Final
from typing import ParamSpec
from typing import TypeAlias

import babel.numbers
from typing_extensions import assert_never

from . import Currency
from . import Money
from . import Overdraft

__all__ = ("format_monetary",)

P = ParamSpec("P")
Monetary: TypeAlias = Money[Currency] | Overdraft[Currency]


# We create the format_monetary function using a wrapper function. This is to be able to
# express the typing relationship between the wrapping and the wrapped function: the
# resulting function accepts an immoney-specific Money or Overdraft as its first
# argument, where the wrapped function takes the numeric value and currency code as
# distinct primitive values.
#
# From a runtime perspective, this dance is entirely unnecessary, so if some mechanism
# should be implemented in the Python type system to express this without a wrapper,
# this can be reduced to a simple non-nested function.
#
# Doing it this way still seems worth it, because it allows entirely "outsourcing" the
# signature of the function parameters to babel, rather than to have lots of duplication
# here that's always under risk of becoming out of sync or stale.
def _wrap_format_function(
    function: Callable[Concatenate[Decimal, str, P], str],
) -> Callable[Concatenate[Monetary, P], str]:
    def format_monetary(
        value: Monetary,
        /,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> str:
        if isinstance(value, Money):
            number = value.decimal
        elif isinstance(value, Overdraft):
            number = -value.decimal
        else:
            assert_never(value)

        return function(
            number,
            value.currency.code,
            *args,
            **kwargs,
        )

    return format_monetary


format_monetary: Final = _wrap_format_function(babel.numbers.format_currency)
