from installies.lib.validate import Validator
from installies.lib.check import (
    EmptyChecker,
    LengthChecker,
    AllowedCharactersChecker,
    DisallowedCharactersChecker,
    UniqueChecker,
    NotInContainerChecker,
    DictionaryChecker,
)
from installies.models.app import App
from installies.models.supported_distros import Distro
from installies.models.discussion import Thread, Comment
from installies.lib.url import make_slug
from installies.config import (
    supported_script_actions,
    supported_distros,
    max_script_length,
    supported_visibility_options,
)

class AppNameValidator(Validator):
    """A class for validating app names submitted by the user."""

    checkers = [
        AllowedCharactersChecker(
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
        AllowedCharactersChecker(
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
        AllowedCharactersChecker(
            allow_extra=['.', '-']
        )
    ]

    data_name = 'Version'


class AppCurrentVersionValidator(VersionValidator):
    """A class to validator app current version strings."""

    data_name = "App current version"

    
class ScriptActionValidator(Validator):
    """A class for validating script actions submitted by the user."""

    checkers = [
        EmptyChecker(),
        AllowedCharactersChecker(
            allow_spaces=False,
            allow_uppercase=False,
            allow_extra=['-']
        ),
        LengthChecker(max_len=32),
    ]

    data_name = 'Script action'


class ScriptDistroValidator(Validator):
    """A class for validating script distros submitted by the user."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=255),
        AllowedCharactersChecker(
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
        AllowedCharactersChecker(
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


class ScriptMethodValidator(Validator):
    """A class for validating script methods."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=255),
        AllowedCharactersChecker(allow_extra=['_', '-', ',', '.']),
    ]

    data_name = 'Script method'


class ScriptVersionValidator(VersionValidator):
    """A class for validating script version strings"""

    data_name = 'Script version'


class ReportTitleValidator(Validator):
    """A class for validating report title."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=64),
        AllowedCharactersChecker(
            allow_extra=['-', ',', '.', '"', '\'', '(', ')'],
        )
    ]
    
    data_name = 'Report title'


class ReportBodyValidator(Validator):
    """A class for validating report body."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=2048),
        AllowedCharactersChecker(
            allow_extra=['-', ',', '.', '"', '\'', '(', ')'],
        )
    ]

    data_name = 'Report body'


class ThreadTitleValidator(Validator):
    """A class for validating topic titles."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=128),
        AllowedCharactersChecker(
            allow_extra=['-', ',', '.', '"', '\'', '(', ')'],
        ),
        UniqueChecker(
            table=Thread,
            column_name='title',
        ),
    ]

    data_name = 'Thread title'


class CommentContentValidator(Validator):
    """A class for validating comment content."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=1024),
        AllowedCharactersChecker(
            allow_extra=['-', ',', '.', '"', '\'', '(', ')'],
        ),
    ]

    data_name = 'Comment content'
