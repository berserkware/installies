from installies.lib.validate import Validator
from installies.lib.check import InContainerChecker, AllowedCharactersChecker, EmptyChecker
from installies.apps.app_manager.models import Distro

class DistroSlugValidator(Validator):
    """A class for validating new distro slugs submitted by admins."""

    checkers = [
        EmptyChecker(),
        AllowedCharactersChecker(
            allow_spaces=False,
            allow_uppercase=False,
            allow_extra=['-']
        ),
        InContainerChecker(container=Distro.get_all_distro_slugs, container_name='supported distros'),
    ]

    data_name = 'Distro slug'


class DistroNameValidatior(Validator):
    """A class for validating new distro names submitted by admins."""

    checkers = [
        EmptyChecker(),
        AllowedCharactersChecker(allow_extra=['!', '-', '_']),
    ]

    data_name = 'Distro name'