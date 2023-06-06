from installies.lib.form import Form, FormInput
from installies.apps.admin.validate import (
    DistroSlugValidator,
    DistroNameValidatior,
)
from installies.apps.app_manager.models import Distro

class CreateDistroForm(Form):
    """A distro for creating distros"""

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
