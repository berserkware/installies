from installies.validators.base import Validator
from installies.validators.check import (
    EmptyChecker,
    LengthChecker,
    CharacterWhitelistChecker,
    CharacterBlacklistChecker,
    UniqueChecker,
    NotInContainerChecker,
    DictionaryChecker,
)
from installies.models.app import App
from installies.lib.url import make_slug

class AppNameValidator(Validator):
    """A class for validating app names submitted by the user."""

    checkers = [
        CharacterWhitelistChecker(
            allow_uppercase=False,
            allow_spaces=False,
            allow_extra=['-', '_']
        ),
        LengthChecker(max_len=64),
        EmptyChecker(),
        UniqueChecker(
            table=App,
            column_name='name',
        ),
    ]

    data_name = 'App name'


class AppDisplayNameValidator(Validator):
    """A class for validating app display names."""

    checkers = [
        CharacterWhitelistChecker(
            allow_extra=['-', '_'],
        ),
        LengthChecker(max_len=64),
    ]

    data_name = 'App display name'
    

class AppDescriptionValidator(Validator):
    """A class for validating app descriptions submitted by the user."""

    checkers = [
        LengthChecker(max_len=1000),
        EmptyChecker(),
    ]

    data_name = 'App description'


class VersionValidator(Validator):
    """A class to validate version strings."""

    checkers = [
        LengthChecker(max_len=64),
        CharacterWhitelistChecker(
            allow_extra=['.', '-']
        )
    ]

    data_name = 'Version'


class AppCurrentVersionValidator(VersionValidator):
    """A class to validator app current version strings."""

    checkers = VersionValidator.checkers + [EmptyChecker()]
    
    data_name = "App current version"
