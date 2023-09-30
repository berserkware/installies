from flask import g
from installies.forms.base import Form, FormInput
from installies.validators.script import (
    ScriptActionValidator,
    ScriptShellValidator,
    ScriptDistroValidator,
    ScriptContentValidator,
    ScriptDistroDictionaryValidator,
    ScriptMethodValidator,
    ScriptVersionValidator,
)
from installies.models.supported_distros import SupportedDistrosJunction
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
            SupportedDistrosJunction.get_from_string,
            '',
        ),
        FormInput('script-content', ScriptContentValidator),
        FormInput(
            'script-method',
            ScriptMethodValidator,
            original_data_getter=lambda script: script.method,
        ),
        FormInput('for-version', ScriptVersionValidator, default=None),
        FormInput('script-use-default-function-matcher', default=None),
    ]
    model = Script


class AddScriptForm(ModifyScriptForm):
    """A form for adding scripts."""

    def save(self, app: App):
        shell = Shell.get(Shell.name == self.data['script-shell'])
        
        return AppScript.create(
            app=app,
            supported_distros=self.data['script-supported-distros'],
            content=self.data['script-content'],
            version=self.data['for-version'],
            actions=self.data['script-actions'],
            shell=shell,
            method=self.data['script-method'],
            submitter=g.user,
            use_default_function_matcher=(True if self.data.get('script-use-default-function-matcher') is not None else False),
        )


class EditScriptForm(ModifyScriptForm):
    """A form for editing scripts."""

    edit_form = True
    
    def save(self):
        shell = Shell.get(Shell.name == self.data['script-shell'])

        print([True if self.data.get('script-use-default-function-matcher') is not None else False])
        
        return self.original_object.edit(
            actions=self.data['script-actions'],
            shell=shell,
            supported_distros=self.data['script-supported-distros'],
            content=self.data['script-content'],
            version=self.data['for-version'],
            method=self.data['script-method'],
            use_default_function_matcher=(True if self.data.get('script-use-default-function-matcher') is not None else False),
        )
