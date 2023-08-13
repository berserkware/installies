from installies.validators.base import Validator
from installies.validators.check import EmptyChecker, LengthChecker

class BanReasonValidator(Validator):
    """A class for validating ban reasons."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=255),
    ]
