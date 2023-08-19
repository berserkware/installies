from installies.models.base import BaseModel
from installies.models.user import User
from installies.models.app import App
from installies.models.script import Script
from installies.models.discussion import Comment
from peewee import (
    CharField,
    DateTimeField,
    TextField,
    ForeignKeyField,
    BooleanField,
)
from datetime import datetime

class Report(BaseModel):
    """A model for reports."""

    title = CharField(255)
    body = TextField()
    report_type = CharField(255)
    creation_date = DateTimeField(default=datetime.now)
    submitter = ForeignKeyField(User, backref="reports")
    resolved = BooleanField(default=False)

    def delete_instance(self):
        if self.report_type == 'app':
            self.app_data.get().delete_instance()
        elif self.report_type == 'script':
            self.script_data.get().delete_instance()
        elif self.report_type == 'comment':
            self.comment_data.get().delete_instance()
        super().delete_instance()


class ReportAppInfo(BaseModel):
    """A model for storing app data for reports."""

    report = ForeignKeyField(Report, backref="app_data")
    app = ForeignKeyField(App, backref="reports")


class ReportScriptInfo(BaseModel):
    """A model for storing script data for reports."""

    report = ForeignKeyField(Report, backref="script_data")
    script = ForeignKeyField(Script, backref="reports")


class ReportCommentInfo(BaseModel):
    """A model for storing comment data for reports."""

    report = ForeignKeyField(Report, backref="comment_data")
    comment = ForeignKeyField(Comment, backref="reports")
