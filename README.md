### Features

There are a few core design aspects of this library that each eliminate entire classes
of bugs:

- Exposed and internal data types are either immutable or faux immutable.
- Invalid amounts of money cannot be represented. There is no such thing as `0.001` US
  dollars, and there is no such thing as negative money.
- Builtin operations do not lose precision. This point is pretty much fall-out of the
  previous point, but still worth mentioning.
- Built from the ground-up with support for static type checking in mind. This means
  that bugs that attempt to mix currencies can be found by a static type checker.

#### Immediate and full instantiation

"2 dollars" is represented exactly the same as "2.00 dollars", in every aspect. This
means that normalization of values happen at instantiation time.

#### Safe division

In real life we cannot split the subunit of a currency, so with our abstractions of
money we shouldn't be able to do that either. Therefor instead of returning a value with
lost precision, the implementation of division for `Money` returns a tuple of new
instances with the value split up as equal as possible.

#### Money fractions

...
