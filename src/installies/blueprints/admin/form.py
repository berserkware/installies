from installies.lib.form import Form, FormInput
from installies.blueprints.admin.validate import (
    DistroSlugValidator,
    DistroNameValidatior,
    ArchitectureNameValidator,
)
from installies.models.supported_distros import Distro, Architecture, AlternativeArchitectureName
from installies.blueprints.admin.converter import get_other_architecture_names_from_string

class CreateDistroForm(Form):
    """A form for creating distros"""

    inputs = [
        FormInput('distro-name', DistroNameValidatior),
        FormInput('distro-slug', DistroSlugValidator),
        FormInput('distro-based-on'),
    ]
    model = Distro

    def save(self, based_on: Distro=None):
        """
        Create the distro.

        :param based_on: The distro that the new distro is based on.
        """

        return Distro.create(
            name=self.data['distro-name'],
            slug=self.data['distro-slug'],
            based_on=based_on
        )


class CreateArchitectureForm(Form):
    """A form for creating architechtures."""

    inputs = [
        FormInput('architecture-name', ArchitectureNameValidator),
        FormInput(
            'architecture-other-names',
            ArchitectureNameValidator,
            get_other_architecture_names_from_string
        ),
    ]
    model = Architecture

    def save(self):
        """Creates the architechture."""

        architechture = Architecture.create(
            name=self.data['architecture-name'],
        )

        for name in self.data['architecture-other-names']:
            AlternativeArchitectureName.create(
                name=name,
                architecture=architecture,
            )

        return Architecture
