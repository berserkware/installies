from flask import g
from installies.forms.base import Form, FormInput
from installies.validators.app import (
    AppNameValidator,
    AppDisplayNameValidator,
    AppDescriptionValidator,
    AppCurrentVersionValidator,
)
from installies.models.app import App


class CreateAppForm(Form):
    """
    A form for creating apps.
    """

    inputs = [
        FormInput('app-name', AppNameValidator, default=''),
        FormInput('app-display-name', AppDisplayNameValidator, default=None),
        FormInput('app-desc', AppDescriptionValidator, default=''),
        FormInput('app-current-version', AppCurrentVersionValidator, default=''),
    ]
    model = App

    def save(self):
        """Creates the app."""
        return App.create(
            name=self.data['app-name'],
            display_name=self.data['app-display-name'],
            description=self.data['app-desc'],
            current_version=self.data['app-current-version'],
            submitter=g.user,
        )


class EditAppForm(Form):
    """
    A form for editing apps.
    """

    inputs = [
        FormInput('app-display-name', AppDisplayNameValidator, default=None),
        FormInput('app-desc', AppDescriptionValidator, default=''),
        FormInput('app-current-version', AppCurrentVersionValidator, default=None),
    ]
    model = App
    edit_form = True

    def save(self, app: App):
        """Edits the app."""
        return app.edit(
            display_name=self.data['app-display-name'],
            description=self.data['app-desc'],
            current_version=self.data['app-current-version'],
        )
