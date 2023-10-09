<h1 align=center>immoney</h1>

<p align=center>
    <a href=https://github.com/antonagestam/immoney/actions?query=workflow%3ACI+branch%3Amain><img src=https://github.com/antonagestam/immoney/workflows/CI/badge.svg alt="CI Build Status"></a>
    <a href=https://codecov.io/gh/antonagestam/immoney><img src=https://codecov.io/gh/antonagestam/immoney/branch/main/graph/badge.svg?token=UEI88N0EPG alt="Test coverage report"></a>
    <br>
    <a href=https://pypi.org/project/immoney/><img src=https://img.shields.io/pypi/v/immoney.svg?color=informational&label=PyPI alt="PyPI Package"></a>
    <a href=https://pypi.org/project/immoney/><img src=https://img.shields.io/pypi/pyversions/immoney.svg?color=informational&label=Python alt="Python versions"></a>
</p>

### Installation

```shell
$ pip install --require-venv immoney
```

### Design goals

There are a few core design aspects of this library that each eliminate entire classes
of bugs:

- Exposed and internal data types are either immutable or faux immutable.
- Invalid amounts of money cannot be represented. There is no such thing as `0.001` US
  dollars, and there is no such thing as negative money.
- Builtin operations never implicitly lose precision.
- Built from the ground-up with support for static type checking in mind. This means
  that bugs that attempt to mix currencies can be found by a static type checker.

### Features

#### Safe division

In real life we cannot split the subunit of a currency, and so for our abstractions to
safely reflect reality, we shouldn't be able to do that in code either. Therefore
instead of defining division to return a value with precision loss, the implementation
of division for `Money` returns a tuple of new instances with the value split up as even
as possible. This is implemented as `Money.__floordiv__`.

```pycon
>>> Money("0.11", SEK) // 3
(Money('0.04', SEK), Money('0.04', SEK), Money('0.03', SEK))
```

This method of division will always be safe, as it has the guaranteed property that the
sum of the instances returned by the operation always equal the original numerator.

#### Subunit fractions

Sometimes we do need to represent fractions of monetary values that are smaller than the
subunit of a currency, for instance as a partial result of a larger equation. For that
purpose, this library exposes a `SubunitFraction` type. This type is used as return type
for `Money.__truediv__`.

```pycon
>>> SEK(13) / 3
SubunitFraction('1300/3', SEK)
```

Because there is no guarantee that a `SubunitFraction` is a whole subunit (by definition
...), converting back to `Money` can only be done with precision loss.

```pycon
>>> (SEK(13) / 3).round_money(Round.DOWN)
Money('4.33', SEK)
```

#### Overdraft

Again referring to real life, there is no such thing as negative money. Following in the
same vein as for not allowing subunits to be split, the value of a `Money` instance
cannot be negative. Instead, to represent for instance a negative balance on an account,
this library exposes an `Overdraft` class that is used as return type of `Money.__sub__`
when the computed value would have been negative.

```pycon
>>> balance = SEK(5)
>>> balance - SEK(4)
Money('1.00', SEK)
>>> balance - SEK(5)
Money('0.00', SEK)
>>> balance - SEK("6.50")
Overdraft('1.50', SEK)
>>> balance - SEK("6.50") + SEK("1.50")
Money('0.00', SEK)
```

Because negative values are encoded as its own type in this way, situations where
negative values can result from arithmetic but aren't logically expected, such as for
the price of an item in a store, can be discovered with a static type checker.

#### Type-safe comparison

Instances of `Money` do not support direct comparison with numeric scalar values. For
convenience an exception is made for integer zero, which is always unambiguous.

```pycon
>>> from immoney.currencies import SEK
>>> SEK(1) == 1
False
>>> SEK(1) >= 1
Traceback (most recent call last):
  ...
TypeError: '>=' not supported between instances of 'Money' and 'int'
>>> SEK(0) == 0
True
```

#### Immediate and full instantiation

"2 dollars" is represented exactly the same as "2.00 dollars", in every aspect. This
means that normalization of values happen at instantiation time.

Instantiating normalizes precision to the number of subunits of the instantiated
currency.

```pycon
>>> EUR(2)
Money('2.00', EUR)
>>> EUR("2.000")
Money('2.00', EUR)
```

Trying to instantiate with a value that would result in precision loss raises a runtime
error.

```pycon
>>> EUR("2.001")
Traceback (most recent call last):
  ...
immoney.errors.ParseError: Cannot interpret value as Money of currency EUR ...
```

#### Instance cache

Since instances of `Money` and `Currency` are immutable it's safe to reuse existing
instances instead of instantiating new ones. This happens transparently when
instantiating a new `Money` instance and can lead to faster code and less consumed
memory.

#### Retrieving currencies by code

Currencies can be retrieved by their codes via `immoney.currencies.registry`.

```pycon
>>> from immoney.currencies import registry
>>> registry["NOK"]
Currency(code=NOK, subunit=100)
>>> registry["MVP"]
Currency(code=MVP, subunit=1)
>>> registry["foo"]
Traceback (most recent call last):
  ...
KeyError: 'foo'
```

#### Custom currency registries

The library ships with a sensible set of default currencies, however, you might want to
use a custom registry for two reasons:

- You want to use non-default currencies.
- You only want to allow a subset of the default currencies.

To achieve this, you can construct a custom set of types. It's recommended to use a
custom abstract base class for this, this way things will also play nice with the
Pydantic integration.

```python
import abc
from typing import Final
from immoney.registry import CurrencyCollector
from immoney.currencies import Currency

__currencies = CurrencyCollector()


class SpaceCurrency(Currency, abc.ABC):
    ...


class MoonCoinType(SpaceCurrency):
    subunit = 100_000
    code = "MCN"


MCN: Final = MoonCoinType()
__currencies.add(MCN)


class JupiterDollarType(SpaceCurrency):
    subunit = 100
    code = "JCN"


JCN: Final = JupiterDollarType()
__currencies.add(JCN)

custom_registry: Final = __currencies.finalize()
```

#### Pydantic V2 support

Install a compatible Pydantic version by supplying the `[pydantic]` extra.

```shell
$ pip install --require-venv immoney[pydantic]
```

The `Currency`, `Money`, `SubunitFraction` and `Overdraft` entities can all be used as
Pydantic model fields.

```pycon
>>> from pydantic import BaseModel
>>> from immoney import Money
>>> from immoney.currencies import USD
>>> class Model(BaseModel, frozen=True):
...     money: Money
>>> print(instance.model_dump_json(indent=2))
{
  "money": {
    "subunits": 25000,
    "currency": "USD"
  }
}
```

### Developing

It's a good idea to use virtualenvs for development. I recommend using a combination of
[pyenv] and [pyenv-virtualenv] for installing Python versions and managing virtualenvs.
Using the lowest supported version for development is recommended, as of writing this is
Python 3.10.

[pyenv]: https://github.com/pyenv/pyenv
[pyenv-virtualenv]: https://github.com/pyenv/pyenv-virtualenv

To install development requirements, run the following with your virtualenv activated.

```shell
$ python3 -m pip install .[pydantic,test]
```

Now, to run the test suite, execute the following.

```shell
$ pytest
```

Static analysis and formatting is configured with [pre-commit].

[pre-commit]: https://pre-commit.com/

```shell
# configure hooks to run when pushing
$ pre-commit install -t pre-push
# or on every commit, if you prefer
$ pre-commit install -t pre-commit
# run all checks
$ pre-commit run --all-files
# or just a single hook
$ pre-commit run mypy --all-files
```
