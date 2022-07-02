class ImmoneyError(Exception):
    ...


class MoneyParseError(ImmoneyError, ValueError):
    ...


class FrozenInstanceError(ImmoneyError, AttributeError):
    ...


class InvalidSubunit(ImmoneyError, ValueError):
    ...


class DivisionByZero(ImmoneyError, ZeroDivisionError):
    ...
