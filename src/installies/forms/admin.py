from installies.forms.base import Form, FormInput
from installies.validators.admin  import (
    BanReasonValidator,
)
from installies.models.user import Ban

class BanUserForm(Form):
    """A form for banning users."""

    inputs = [
        FormInput('reason', BanReasonValidator),
    ]
    model = Ban

    def save(self, user):
        """Creates the Ban."""

        return Ban.create(
            user=user,
            reason=self.data['reason'],
        )
