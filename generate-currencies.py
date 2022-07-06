import pathlib
from typing import Iterator

from moneyed.classes import CURRENCIES

currencies_file = pathlib.Path("src/immoney/currencies.py")
imports_template = """\
from __future__ import annotations

from typing import Final

from . import Currency
"""
currency_template = """

class {code}Type(Currency):
    code = "{code}"
    subunit = {subunit}


{code}: Final = {code}Type()
"""


def generate_code() -> Iterator[str]:
    yield imports_template
    for currency in CURRENCIES.values():
        yield currency_template.format(code=currency.code, subunit=currency.sub_unit)


with currencies_file.open("w") as file:
    for chunk in generate_code():
        file.write(chunk)
