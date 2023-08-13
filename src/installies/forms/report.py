from flask import g
from installies.lib.form import Form, FormInput
from installies.validators.report import (
    ReportTitleValidator,
    ReportBodyValidator,
)
from installies.models.app import App
from installies.models.script import Script
from installies.models.report import AppReport, ScriptReport

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
