from flask import g
from installies.lib.form import Form, FormInput
from installies.validators.report import (
    ReportTitleValidator,
    ReportBodyValidator,
)
from installies.models.app import App
from installies.models.script import Script
from installies.models.report import Report, ReportAppInfo, ReportScriptInfo

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
        report = Report.create(
            title=self.data['title'],
            body=self.data['body'],
            report_type='app',
            submitter=g.user,
        )
        info = ReportAppInfo.create(
            report=report,
            app=app
        )
        return report


class ReportScriptForm(CreateReportBaseForm):
    """A form to report scripts."""

    model = Script

    def save(self, script: Script):
        report = Report.create(
            title=self.data['title'],
            body=self.data['body'],
            report_type='script',
            submitter=g.user,
            script=script,
        )
        info = ReportScriptInfo.create(
            report=report,
            script=script,
        )
        return report
