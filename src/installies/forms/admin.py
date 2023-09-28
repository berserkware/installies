from installies.forms.base import Form, FormInput
from installies.validators.admin  import (
    BanReasonValidator,
    ShellNameValidator,
    ShellFileExtensionValidator,
    ShellFileMimetypeValidator,
    ShellInterpreterPathValidator,
    ShellInterpreterArgValidator,
    ShellFunctionMatcherStartValidator,
    ShellFunctionMatcherBlockValidator,
    ShellFunctionMatcherEndValidator,
)
from installies.models.user import Ban
from installies.models.script import Shell

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


class ModifyShellForm(Form):
    """A form for modifying shells."""
    
    inputs = [
        FormInput(
            'shell-name',
            ShellNameValidator,
            original_data_getter=lambda shell: shell.name,
        ),
        FormInput('shell-file-extension', ShellFileExtensionValidator),
        FormInput('shell-file-mimetype', ShellFileMimetypeValidator),
        FormInput('shell-interpreter-path', ShellInterpreterPathValidator),
        FormInput('shell-interpreter-arg', ShellInterpreterArgValidator, default=''),
        FormInput('shell-function-matcher-start', ShellFunctionMatcherStartValidator, default=''),
        FormInput('shell-function-matcher-block', ShellFunctionMatcherBlockValidator),
        FormInput('shell-function-matcher-end', ShellFunctionMatcherEndValidator),
    ]
    model = Shell


class CreateShellForm(ModifyShellForm):
    """A form for creating shells."""
        
    def save(self):
        return Shell.create(
            name=self.data['shell-name'],
            file_extension=self.data['shell-file-extension'],
            file_mimetype=self.data['shell-file-mimetype'],
            interpreter_path=self.data['shell-interpreter-path'],
            interpreter_arg=self.data['shell-interpreter-arg'],
            function_matcher_start=self.data['shell-function-matcher-start'].replace('\r', ''),
            function_matcher_block=self.data['shell-function-matcher-block'].replace('\r', ''),
            function_matcher_end=self.data['shell-function-matcher-end'].replace('\r', ''),
        )


class EditShellForm(ModifyShellForm):
    """A form for editing shells."""

    edit_form = True
    
    def save(self, shell: Shell):
        shell.name = self.data['shell-name']
        shell.file_extension = self.data['shell-file-extension']
        shell.file_mimetype = self.data['shell-file-mimetype']
        
        shell.interpreter_path = self.data['shell-interpreter-path']
        shell.interpreter_arg = self.data['shell-interpreter-arg']

        shell.function_matcher_start = self.data['shell-function-matcher-start'].replace('\r', '')
        shell.function_matcher_block = self.data['shell-function-matcher-block'].replace('\r', '')
        shell.function_matcher_end = self.data['shell-function-matcher-end'].replace('\r', '')

        shell.use_default_function_matcher = [
            True if self.data['script-use-default-function-matcher'] is 'yes' else False
        ],

        return shell.save()
