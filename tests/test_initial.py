from immoney import Money
from immoney._base import Debt
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

    assert m - 2 * m == Debt(m)
