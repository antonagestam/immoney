from decimal import Decimal
from fractions import Fraction

from immoney import Money
from immoney import Overdraft
from immoney import Round
from immoney import SubunitFraction
from immoney.currencies import SEK


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
