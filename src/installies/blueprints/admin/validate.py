from installies.lib.validate import Validator
from installies.lib.check import EmptyChecker, LengthChecker

class BanReasonValidator(Validator):
    """A class for validating ban reasons."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=255),
    ]
