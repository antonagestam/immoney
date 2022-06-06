from decimal import Decimal
from fractions import Fraction

import pytest

from immoney import Money
from immoney import Overdraft
from immoney import Round
from immoney import SubunitFraction
from immoney.currencies import NOK
from immoney.currencies import SEK


def test_embryo_of_a_suite():
    m = Money("5.37", SEK)
    a, b = m / 2
    assert a == Money("2.69", SEK)
    assert b == Money("2.68", SEK)

    assert a > b
    assert not a < b
    assert b < a
    assert not b > a

    assert a + b == m

    a, b, c, d = m / 4
    assert a == Money("1.35", SEK)
    assert b == Money("1.34", SEK)
    assert c == Money("1.34", SEK)
    assert d == Money("1.34", SEK)
    assert a + b + c + d == m

    # nok = Money(1, NOK)
    # reveal_type(NOK)
    # reveal_type(nok)
    # reveal_type(m)
    # nok + m  # should give type error :)
    # nok + nok
    # m + m

    assert m - 2 * m == Overdraft(m)


def test_convenience():
    assert NOK(123) == Money(123, NOK)
    assert SEK("23.50") == Money("23.50", SEK)
    assert NOK.zero == Money("0.00", NOK)
    assert SEK.zero == Money("0.00", SEK)


def test_random_comparisons():
    # Money can be compared with 0, but not to other ints
    n = Money(1, SEK)
    z = Money(0, SEK)
    assert n != 0
    assert n != 1
    assert z == 0
    assert z != 1


def test_multiplication():
    # Multiplication with decimal results in fraction.
    m = Money("23.34", SEK)
    v = m * Decimal("23.89")
    assert isinstance(v, SubunitFraction)
    assert v == SubunitFraction(Fraction(2787963, 50), SEK)

    # The fraction can be rounded, with loss of precision
    r = v.round(Round.DOWN)
    assert isinstance(r, Money)
    assert r == Money("557.59", SEK)

    # SubunitFraction can be compared with Money :)
    fr = SubunitFraction.from_money(m, 1)
    assert fr == m
    assert fr == SubunitFraction.from_money(m, 1)
    assert fr != SubunitFraction.from_money(m, 2)

    # Multiplication with int results in new Money
    intmul = m * 24
    assert isinstance(intmul, Money)
    assert intmul == Money("560.16", SEK)


def test_subtraction():
    # When the result of subtraction is positive, nothing extraordinary happens.
    m = Money("100", SEK)
    subbed = m - Money("75.23", SEK)
    assert subbed == Money("24.77", SEK)

    assert Money(1, SEK) - Money(1, SEK) == Money(0, SEK)

    # When the result of subtraction exceeds zero, the resulting value is an instance of
    # Overdraft.
    overdraft = m - Money("100.01", SEK)
    assert overdraft == Overdraft(Money(".01", SEK))

    redeemed = overdraft + SEK("0.01")
    assert redeemed == SEK(0)

    larger_overdraft = Overdraft(SEK(1000))
    not_yet_redeemed = larger_overdraft + SEK(501)
    assert not_yet_redeemed == Overdraft(SEK(499))

    growing_overdraft = larger_overdraft + Overdraft(SEK(10000))
    assert growing_overdraft == Overdraft(SEK(11000))


def test_currency_immutable():
    with pytest.raises(AttributeError):
        # TODO: Test this type error
        SEK.foo = "bar"  # type: ignore[assignment]
    with pytest.raises(AttributeError):
        # TODO: Test this type error
        SEK.code = "bar"  # type: ignore[misc]
    with pytest.raises(AttributeError):
        # TODO: Test this type error
        SEK.subunit = 1000  # type: ignore[misc]
    assert SEK.code == "SEK"
    assert SEK.subunit == 100
