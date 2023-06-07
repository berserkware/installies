from installies.lib.form import Form, FormInput
from installies.apps.admin.validate import (
    DistroSlugValidator,
    DistroNameValidatior,
    ArchitechtureNameValidator,
)
from installies.apps.app_manager.models import Distro, Architechture, AlternativeArchitechtureName
from installies.apps.admin.converter import get_other_architechture_names_from_string

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


class CreateArchitechtureForm(Form):
    """A form for creating architechtures."""

    inputs = [
        FormInput('architechture-name', ArchitechtureNameValidator),
        FormInput(
            'architechture-other-names',
            ArchitechtureNameValidator,
            get_other_architechture_names_from_string
        ),
    ]
    model = Architechture

    def save(self):
        """Creates the architechture."""

        architechture = Architechture.create(
            name=self.data['architechture-name'],
        )

        for name in self.data['architechture-other-names']:
            AlternativeArchitechtureName.create(
                name=name,
                architechture=architechture,
            )

        return Architechture
