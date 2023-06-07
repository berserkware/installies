from flask import g
from installies.lib.form import Form, FormInput
from installies.blueprints.app_manager.validate import (
    AppNameValidator,
    AppDescriptionValidator,
    AppVisibilityValidator,
    ScriptActionValidator,
    ScriptDistroValidator,
    ScriptContentValidator,
)
from installies.blueprints.app_manager.upload import get_distros_from_string
from installies.blueprints.app_manager.models import App, Script

class CreateAppForm(Form):
    """
    A form for creating apps.
    """

    inputs = [
        FormInput('app-name', AppNameValidator, default=''),
        FormInput('app-desc', AppDescriptionValidator, default='')
    ]
    model = App

    def save(self):
        """Creates the app."""
        return App.create(
            name=self.data['app-name'],
            description=self.data['app-desc'],
            submitter=g.user,
        )


class EditAppForm(Form):
    """
    A form for editing apps.
    """

    inputs = [
        FormInput('app-desc', AppDescriptionValidator, default='')
    ]
    model = App

    def save(self):
        """Edits the app."""
        return App.edit(
            description=self.data['app-desc']
        )


class ChangeAppVisibilityForm(Form):
    """
    A form for changing the visibility of apps.
    """

    inputs = [
        FormInput('visibility', AppVisibilityValidator)
    ]
    model = App

    def save(self, app: App):
        """Changes the app visibility."""
        app.visibility = self.data['visibility']
        app.save()
        return app


class ModifyScriptForm(Form):
    """
    A form for adding or editing scripts.
    """

    inputs = [
        FormInput('script-action', ScriptActionValidator, default=''),
        FormInput(
            'script-supported-distros',
            ScriptDistroValidator,
            get_distros_from_string,
            '',
        ),
        FormInput('script-content', ScriptContentValidator)
    ]
    model = Script


class AddScriptForm(ModifyScriptForm):
    """A form for adding scripts."""

    def save(self, app: App):
        return Script.create(
            action=self.data['script-action'],
            supported_distros=self.data['script-supported-distros'],
            content=self.data['script-content'],
            app=app
        )


class EditScriptForm(ModifyScriptForm):
    """A form for editing scripts."""

    def save(self, script: Script):
        return script.edit(
            action=self.data['script-action'],
            supported_distros=self.data['script-supported-distros'],
            content=self.data['script-content'],
        )
