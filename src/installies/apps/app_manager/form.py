from installies.lib.form import Form, FormInput
from installies.apps.app_manager.validate import (
    AppNameValidator,
    AppDescriptionValidator,
    AppVisibilityValidator,
    ScriptActionValidator,
    ScriptDistroValidator,
    ScriptContentValidator,
)
from installies.apps.app_manager.upload import get_distros_from_string

class CreateAppForm(Form):
    """
    A form for creating apps.
    """

    inputs = [
        FormInput('app-name', AppNameValidator, default=''),
        FormInput('app-desc', AppDescriptionValidator, default='')
    ]


class EditAppForm(Form):
    """
    A form for editing apps.
    """

    inputs = [
        FormInput('app-desc', AppDescriptionValidator, default='')
    ]


class ChangeAppVisibilityForm(Form):
    """
    A form for changing the visibility of apps.
    """

    inputs = [
        FormInput('visibility', AppVisibilityValidator)
    ]


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
