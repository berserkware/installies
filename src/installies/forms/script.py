from flask import g
from installies.forms.base import Form, FormInput
from installies.validators.script import (
    ScriptActionValidator,
    ScriptShellValidator,
    ScriptDistroValidator,
    ScriptContentValidator,
    ScriptDistroDictionaryValidator,
    ScriptDescriptionValidator,
    ScriptVersionValidator,
)
from installies.models.supported_distros import SupportedDistro
from installies.models.app import App
from installies.models.script import AppScript, Script, Shell


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
            'script-shell',
            ScriptShellValidator,
        ),
        FormInput(
            'script-supported-distros',
            ScriptDistroDictionaryValidator,
            SupportedDistro.get_dict_from_string,
            '',
        ),
        FormInput('script-content', ScriptContentValidator),
        FormInput(
            'script-description',
            ScriptDescriptionValidator,
            original_data_getter=lambda script: script.description,
        ),
        FormInput('for-version', ScriptVersionValidator, default=None),
        FormInput('script-use-default-function-matcher', default=None),
    ]
    model = Script


class CreateScriptForm(ModifyScriptForm):
    """A form for creating Scripts."""

    def save(self):
        shell = Shell.get(Shell.name == self.data['script-shell'])

        script = Script.create(
            content=self.data['script-content'],
            actions=self.data['script-actions'],
            shell=shell,
            description=self.data['script-description'],
            submitter=g.user,
            use_default_function_matcher=(True if self.data.get('script-use-default-function-matcher') is not None else False),
        )

        distros = SupportedDistro.create_from_dict(script, self.data['script-supported-distros'])

        return script


class CreateAppScriptForm(CreateScriptForm):
    """A form for creating AppScripts"""

    model = AppScript

    def save(self, app: App):
        script = super().save()

        return AppScript.create(
            script=script,
            app=app,
            version=self.data['for-version'],
        )


class EditScriptForm(ModifyScriptForm):
    """A form for editing Scripts."""

    edit_form = True
    
    def save(self, script: Script):
        shell = Shell.get(Shell.name == self.data['script-shell'])

        for distro in script.supported_distros:
            distro.delete_instance()
        SupportedDistro.create_from_dict(
            script,
            self.data['script-supported-distros']
        )
        
        return script.edit(
            actions=self.data['script-actions'],
            shell=shell,
            content=self.data['script-content'],
            version=self.data['for-version'],
            description=self.data['script-description'],
            use_default_function_matcher=(True if self.data.get('script-use-default-function-matcher') is not None else False),
        )
