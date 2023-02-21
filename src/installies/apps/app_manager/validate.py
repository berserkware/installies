from installies.lib.validate import Validator
from installies.lib.check import (
    EmptyChecker,
    LengthChecker,
    AllowedCharactersChecker,
    DisallowedCharactersChecker,
    ExistsInDatabaseChecker,
    NotInContainerChecker,
)
from installies.database.models import App
from installies.lib.url import make_slug
from installies.globals import supported_script_actions, supported_distros

class AppNameValidator(Validator):
    """A class for validating app names submitted by the user."""

    checkers = [
        AllowedCharactersChecker(
            allow_extra=['-', '_', '<', '>', '!']
        ),
        LengthChecker(max_len=64),
        EmptyChecker(),
        ExistsInDatabaseChecker(
            table=App,
            column_name='slug',
            data_modifier=make_slug
        ),
    ]

    data_name = 'App name'


class AppDescriptionValidator(Validator):
    """A class for validating app descriptions submitted by the user."""

    checkers = [
        LengthChecker(max_len=1000),
        EmptyChecker(),
    ]

    data_name = 'App description'


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
        NotInContainerChecker(
            container=supported_distros,
            container_name='the supported linux distributions'
        )
    ]

    data_name = 'Script distro'


