from fractions import Fraction

from pydantic import BaseModel

from immoney import Currency
from immoney import Money
from immoney import Overdraft
from immoney import SubunitFraction
from immoney import currencies


def test_pydantic():
    class Model(BaseModel, arbitrary_types_allowed=True):
        foo: Currency

    instance = Model.model_validate({"foo": "NOK"})

    assert isinstance(instance, Model)
    assert instance.foo is currencies.NOK

    class Mon(BaseModel, arbitrary_types_allowed=True):
        foo: Money

    instance = Mon.model_validate(
        {
            "foo": {
                "subunits": 4990,
                "currency": "USD",
            }
        }
    )
    assert instance.foo == currencies.USD("49.90")

    class Frac(BaseModel, arbitrary_types_allowed=True):
        value_field: SubunitFraction

    instance = Frac.model_validate(
        {
            "value_field": {
                "numerator": 5,
                "denominator": 3,
                "currency": "INR",
            }
        }
    )
    assert instance.value_field == currencies.INR.fraction(Fraction(5, 3))
    assert instance.model_dump() == {
        "value_field": {
            "numerator": 5,
            "denominator": 3,
            "currency": "INR",
        }
    }

    instance = Frac.model_validate(
        {
            "value_field": {
                "numerator": -5,
                "denominator": 3,
                "currency": "INR",
            }
        }
    )
    assert instance.value_field == currencies.INR.fraction(Fraction(-5, 3))

    instance = Frac.model_validate(
        {
            "value_field": {
                "numerator": -5,
                "denominator": -3,
                "currency": "INR",
            }
        }
    )
    assert instance.value_field == currencies.INR.fraction(Fraction(5, 3))

    class Deficit(BaseModel, arbitrary_types_allowed=True):
        bar: Overdraft

    instance = Deficit.model_validate(
        {
            "bar": {
                "deficit_subunits": 89999,
                "currency": "CUP",
            }
        }
    )
    assert instance.bar == currencies.CUP.overdraft("899.99")
