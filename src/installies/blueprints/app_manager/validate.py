from installies.lib.validate import Validator
from installies.lib.check import (
    EmptyChecker,
    LengthChecker,
    AllowedCharactersChecker,
    DisallowedCharactersChecker,
    ExistsInDatabaseChecker,
    NotInContainerChecker,
    DictionaryChecker,
)
from installies.models.app import App
from installies.models.supported_distros import Distro
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
        ExistsInDatabaseChecker(
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
        ExistsInDatabaseChecker(
            table=App,
            column_name='display_name',
        ),
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


class AppVersionRegexValidator(Validator):
    """A class to validate app version regex validator"""

    checkers = [
        LengthChecker(max_len=256),
        AllowedCharactersChecker(
            allow_extra=[
                '.', '^', '$', '*', '+', '?', '{', '}', '[', ']', '(', ')', '\\', '|', '/', '-', ':', '<', '>'
            ]
        )
    ]

    data_name = 'App version regex'
    

class AppVisibilityValidator(Validator):
    """A class for validating visibility options submitted by the user."""

    checkers = [
        EmptyChecker(),
        NotInContainerChecker(
            container=supported_visibility_options,
            container_name='the supported visibility options'
        ),
    ]

    data_name = 'Visibility option'

    
class ScriptActionValidator(Validator):
    """A class for validating script actions submitted by the user."""

    checkers = [
        EmptyChecker(),
        NotInContainerChecker(
            container=supported_script_actions,
            container_name='the supported script actions'
        ),
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


class ScriptArchitechtureValidator(Validator):
    """A class for validating script architechtures submiited by users."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=255),
        AllowedCharactersChecker(
            allow_spaces=False,
            allow_uppercase=False,
            allow_extra=['-', '_', '*'],
        ),
    ]

    data_name = 'Script architechture'


class ScriptDistroDictionaryValidator(Validator):
    """A class for validating the dictionarys containing the distros and their architechtures."""

    checkers = [
        EmptyChecker(),
        DictionaryChecker(
            key_validator=ScriptDistroValidator,
            value_validator=ScriptArchitechtureValidator,
        ),
    ]
    

class ScriptContentValidator(Validator):
    """A class for validating script content submitted by the user."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=max_script_length),
    ]

    data_name = 'Script content'


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
