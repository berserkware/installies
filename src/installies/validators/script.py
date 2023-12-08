from installies.validators.base import Validator
from installies.validators.check import (
    EmptyChecker,
    LengthChecker,
    CharacterWhitelistChecker,
    CharacterBlacklistChecker,
    UniqueChecker,
    NotInContainerChecker,
    DictionaryChecker,
    NotInContainerChecker,
)
from installies.validators.app import VersionValidator
from installies.models.app import App
from installies.models.script import Script, AppScript
from installies.lib.shell import Shell
from installies.config import (
    max_script_length,
)


class ScriptActionValidator(Validator):
    """A class for validating script actions submitted by the user."""

    checkers = [
        EmptyChecker(),
        CharacterWhitelistChecker(
            allow_spaces=False,
            allow_uppercase=False,
            allow_extra=['-']
        ),
        LengthChecker(max_len=32),
    ]

    data_name = 'Script action'


class ScriptShellValidator(Validator):
    """A class for validating script shells submitted by the user."""

    checkers = [
        EmptyChecker(),
        NotInContainerChecker(
            container=Shell.get_all_names,
            container_name='Supported Shells',
        )
    ]

    data_name = 'Script shell'


class ScriptDistroValidator(Validator):
    """A class for validating script distros submitted by the user."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=255),
        CharacterWhitelistChecker(
            allow_spaces=False,
            allow_uppercase=False,
            allow_extra=['-', '_', '!', '*'],
        ),
    ]

    data_name = 'Script distro'


class ScriptArchitectureValidator(Validator):
    """A class for validating script architectures submiited by users."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=255),
        CharacterWhitelistChecker(
            allow_spaces=False,
            allow_uppercase=False,
            allow_extra=['-', '_', '*'],
        ),
    ]

    data_name = 'Script architecture'


class ScriptDistroDictionaryValidator(Validator):
    """A class for validating the dictionarys containing the distros and their architectures."""

    checkers = [
        EmptyChecker(),
        DictionaryChecker(
            key_validator=ScriptDistroValidator,
            value_validator=ScriptArchitectureValidator,
        ),
    ]
    

class ScriptContentValidator(Validator):
    """A class for validating script content submitted by the user."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=max_script_length),
    ]

    data_name = 'Script content'


class ScriptDescriptionValidator(Validator):
    """A class for validating script descriptions."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=255),
        CharacterWhitelistChecker(allow_extra=['_', '-', ',', '.']),
    ]

    data_name = 'Script description'


class ScriptVersionValidator(VersionValidator):
    """A class for validating script version strings"""

    data_name = 'Script version'
