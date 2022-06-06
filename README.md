### Features

There are a few core design aspects of this library that each eliminate entire classes
of bugs:

- Exposed and internal data types are either immutable or faux immutable.
- Invalid amounts of money cannot be represented. There is no such thing as `0.001` US
  dollars, and there is no such thing as negative money.
- Builtin operations never implicitly lose precision. This point is pretty much fall-out
  of the previous point, but still worth mentioning.
- Built from the ground-up with support for static type checking in mind. This means
  that bugs that attempt to mix currencies can be found by a static type checker.

#### Safe division

In real life we cannot split the subunit of a currency, and so for our abstractions to
safely reflect reality, we shouldn't be able to do that in code either. Therefor instead
of defining division to return a value with precision loss, the implementation of
division for `Money` returns a tuple of new instances with the value split up as even as
possible.

```pycon
>>> Money("0.11", SEK) / 3
(Money('0.04', SEK), Money('0.04', SEK), Money('0.03', SEK))
```

#### Money fractions

...

#### Overdraft

...

#### Type-safe comparison

Instances of `Money` do not support direct comparison with numeric scalar values. For
convenience an exception is made for integer zero, which is always unambiguous.

#### Immediate and full instantiation

"2 dollars" is represented exactly the same as "2.00 dollars", in every aspect. This
means that normalization of values happen at instantiation time.