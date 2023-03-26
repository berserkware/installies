from installies.lib.validate import Validator
from installies.lib.check import (
    EmptyChecker,
    LengthChecker,
    AllowedCharactersChecker,
    DisallowedCharactersChecker,
    ExistsInDatabaseChecker,
    NotInContainerChecker,
)
from installies.apps.app_manager.models import App
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
        NotInContainerChecker(
            container=supported_distros,
            container_name='the supported linux distributions'
        )
    ]

    data_name = 'Script distro'
    

class ScriptContentValidator(Validator):
    """A class for validating script content submitted by the user."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=max_script_length),
    ]

    data_name = 'Script content'
