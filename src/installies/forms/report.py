from flask import g
from installies.lib.form import Form, FormInput
from installies.validators.report import (
    ReportTitleValidator,
    ReportBodyValidator,
)
from installies.models.app import App
from installies.models.script import Script
from installies.models.discussion import Comment
from installies.models.report import Report, ReportAppInfo, ReportScriptInfo, ReportCommentInfo

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
        )
        info = ReportScriptInfo.create(
            report=report,
            script=script,
        )
        return report

class ReportCommentForm(CreateReportBaseForm):
    """A form to report comments."""

    model = Comment

    def save(self, comment: Comment):
        report = Report.create(
            title=self.data['title'],
            body=self.data['body'],
            report_type='comment',
            submitter=g.user,
        )
        info = ReportCommentInfo.create(
            report=report,
            comment=comment,
        )
        return report
