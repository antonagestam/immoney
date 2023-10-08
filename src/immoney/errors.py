class ImmoneyError(Exception):
    ...


class ParseError(ImmoneyError, ValueError):
    ...


class InvalidOverdraftValue(ParseError):
    ...


class FrozenInstanceError(ImmoneyError, AttributeError):
    ...


class InvalidSubunit(ImmoneyError, ValueError):
    ...


class DivisionByZero(ImmoneyError, ZeroDivisionError):
    ...
