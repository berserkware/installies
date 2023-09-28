from installies.validators.base import Validator
from installies.validators.check import (
    EmptyChecker,
    LengthChecker,
    CharacterWhitelistChecker,
    UniqueChecker,
)
from installies.models.script import Shell

class BanReasonValidator(Validator):
    """A class for validating ban reasons."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=255),
    ]

    data_name = 'Ban reason'


class ShellNameValidator(Validator):
    """A class to validate shell names."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=64),
        CharacterWhitelistChecker(
            allow_spaces=False,
            allow_uppercase=False,
            allow_extra=['-', '_'],
        ),
        UniqueChecker(
            Shell,
            'name',
        )
    ]

    data_name = 'Shell name'

    
class ShellFileExtensionValidator(Validator):
    """A class to validate shell file extensions."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=8),
        CharacterWhitelistChecker(
            allow_spaces=False,
            allow_uppercase=False,
        )
    ]

    data_name = 'Shell file extension'

    
class ShellFileMimetypeValidator(Validator):
    """A class to validate shell file mimetypes."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=64),
        CharacterWhitelistChecker(
            allow_spaces=False,
            allow_uppercase=False,
            allow_extra=['-', '_', '/']
        )
    ]

    data_name = 'Shell file mimetype'

    
class ShellInterpreterPathValidator(Validator):
    """A class to validate shell interpreter paths."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=64),
        CharacterWhitelistChecker(
            allow_spaces=False,
            allow_uppercase=False,
            allow_extra=['-', '_', '/'],
        )
    ]

    data_name = 'Shell interpreter path'
    
    
class ShellInterpreterArgValidator(Validator):
    """A class to validate interpreter args."""

    checkers = [
        LengthChecker(max_len=32),
        CharacterWhitelistChecker(
            allow_spaces=False,
            allow_uppercase=False,
            allow_extra=['-', '_', '/'],
        )
    ]

    data_name = 'Shell interpreter path'


class ShellFunctionMatcherStartValidator(Validator):
    """A class to validate shell function matcher start code."""

    checkers = [
        LengthChecker(max_len=256),
    ]

    data_name = 'Shell function matcher start'

class ShellFunctionMatcherBlockValidator(Validator):
    """A class to validate shell function matcher block code."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=256),
    ]

    data_name = 'Shell function matcher block'
    
class ShellFunctionMatcherEndValidator(Validator):
    """A class to validate shell function matcher end code."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=256),
    ]

    data_name = 'Shell function matcher end'
