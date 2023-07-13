from installies.lib.validate import Validator
from installies.lib.check import InContainerChecker, AllowedCharactersChecker, EmptyChecker
from installies.models.supported_distros import Distro

class DistroSlugValidator(Validator):
    """A class for validating new distro slugs submitted by admins."""

    checkers = [
        EmptyChecker(),
        AllowedCharactersChecker(
            allow_spaces=False,
            allow_uppercase=False,
            allow_extra=['-', '_', '!']
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


class ArchitectureNameValidator(Validator):
    """A class for validating new architecture names."""

    checkers = [
        EmptyChecker(),
        AllowedCharactersChecker(
            allow_spaces=False,
            allow_uppercase=False,
            allow_extra=['-', '_']
        ),
    ]

    data_name = 'Architecture name'
