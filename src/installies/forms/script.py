from flask import g
from installies.lib.form import Form, FormInput
from installies.validators.script import (
    ScriptActionValidator,
    ScriptDistroValidator,
    ScriptContentValidator,
    ScriptDistroDictionaryValidator,
    ScriptMethodValidator,
    ScriptVersionValidator,
)
from installies.models.supported_distros import SupportedDistrosJunction
from installies.models.app import App
from installies.models.script import Script


class ModifyScriptForm(Form):
    """
    A form for adding or editing scripts.
    """

    inputs = [
        FormInput(
            'script-actions',
            ScriptActionValidator,
            lambda action_string: [x.strip() for x in action_string.split(',')],
            default='',
        ),
        FormInput(
            'script-supported-distros',
            ScriptDistroDictionaryValidator,
            SupportedDistrosJunction.get_from_string,
            '',
        ),
        FormInput('script-content', ScriptContentValidator),
        FormInput('script-method', ScriptMethodValidator),
        FormInput('for-version', ScriptVersionValidator, default=None)
    ]
    model = Script


class AddScriptForm(ModifyScriptForm):
    """A form for adding scripts."""

    def save(self, app: App):
        return Script.create(
            supported_distros=self.data['script-supported-distros'],
            content=self.data['script-content'],
            app=app,
            version=self.data['for-version'],
            actions=self.data['script-actions'],
            method=self.data['script-method'],
            submitter=g.user,
        )


class EditScriptForm(ModifyScriptForm):
    """A form for editing scripts."""

    def save(self, script: Script):
        return script.edit(
            actions=self.data['script-actions'],
            supported_distros=self.data['script-supported-distros'],
            content=self.data['script-content'],
            version=self.data['for-version'],
            method=self.data['script-method'],
        )
