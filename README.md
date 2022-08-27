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
as possible.

```pycon
>>> Money("0.11", SEK) / 3
(Money('0.04', SEK), Money('0.04', SEK), Money('0.03', SEK))
```

This method of division will always be safe, as it has the guaranteed property that the
sum of the instances returned by the operation always equal the original numerator.

#### Subunit fractions

Sometimes we do need to represent fractions of monetary values that are smaller than the
subunit of a currency, for instance as a partial result of a larger equation. For that
purpose, this library exposes a `SubunitFraction` type. This type is used as return type
for `Money.__floordiv__`.

```pycon
>>> SEK(13) // 3
SubunitFraction('1300/3', SEK)
```

Because there is no guarantee that a `SubunitFraction` is a whole subunit (by definition
...), converting back to `Money` can only be done with precision loss.

```pycon
>>> (SEK(13) // 3).round_money(Round.DOWN)
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

#### Immediate and full instantiation

"2 dollars" is represented exactly the same as "2.00 dollars", in every aspect. This
means that normalization of values happen at instantiation time.

#### Instance cache

Since instances of `Money` and `Currency` are immutable it's safe to reuse existing
instances instead of instantiating new ones. This happens transparently when
instantiating a new `Money` instance and can lead to faster code and less consumed
memory.
