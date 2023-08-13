from flask import g
from installies.lib.form import Form, FormInput
from installies.validators.app import (
    AppNameValidator,
    AppDisplayNameValidator,
    AppDescriptionValidator,
    AppCurrentVersionValidator,
)
from installies.validators.script import (
    ScriptActionValidator,
    ScriptDistroValidator,
    ScriptContentValidator,
    ScriptDistroDictionaryValidator,
    ScriptMethodValidator,
    ScriptVersionValidator,
)
from installies.validators.discussion import (
    ThreadTitleValidator,
    CommentContentValidator,
)
from installies.validators.report import (
    ReportTitleValidator,
    ReportBodyValidator,
)
from installies.blueprints.app_manager.upload import get_distros_from_string
from installies.models.app import App
from installies.models.script import Script
from installies.models.report import AppReport, ScriptReport
from installies.models.discussion import Thread, Comment

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

    def save(self, app):
        """Edits the app."""
        return app.edit(
            display_name=self.data['app-display-name'],
            description=self.data['app-desc'],
            current_version=self.data['app-current-version'],
        )


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
            get_distros_from_string,
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


class CreateReportBaseForm(Form):
    """A form to create reports."""
    
    inputs = [
        FormInput('title', ReportTitleValidator),
        FormInput('body', ReportBodyValidator),
    ]


class ReportAppForm(CreateReportBaseForm):
    """A form to report apps."""

    model = App

    def save(self, app: App):
        return AppReport.create(
            title=self.data['title'],
            body=self.data['body'],
            submitter=g.user,
            app=app,
        )


class ReportScriptForm(CreateReportBaseForm):
    """A form to report scripts."""

    model = Script

    def save(self, script: Script):
        return ScriptReport.create(
            title=self.data['title'],
            body=self.data['body'],
            submitter=g.user,
            script=script,
        )


class CreateThreadForm(Form):
    """A form to create threads."""

    inputs = [
        FormInput('title', ThreadTitleValidator)
    ]
    
    model = Thread

    def save(self, app: App):
        return Thread.create(
            title=self.data['title'],
            app=app,
            creator=g.user,
        )


class CommentForm(Form):
    """A base form for creating or editing comments."""

    inputs = [
        FormInput('content', CommentContentValidator)
    ]

    model = Comment

    
class CreateCommentForm(CommentForm):
    """A form to create comments."""

    def save(self, thread: Thread):
        return Comment.create(
            thread=thread,
            creator=g.user,
            content=self.data['content'],
        )


class EditCommentForm(CommentForm):
    """A form to edit comments"""

    def save(self, comment: Comment):
        comment.content = self.data['content']
        comment.edited = True
        comment.save()
        return comment
