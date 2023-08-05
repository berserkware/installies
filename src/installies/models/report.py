from installies.models.base import BaseModel
from installies.models.user import User
from installies.models.app import App
from installies.models.script import Script
from peewee import (
    CharField,
    DateTimeField,
    TextField,
    ForeignKeyField,
    BooleanField,
)
from datetime import datetime

class ReportBase(BaseModel):
    """A base model for reports."""

    title = CharField(255)
    body = TextField()
    creation_date = DateTimeField(default=datetime.now)
    submitter = ForeignKeyField(User, backref="reports")
    resolved = BooleanField(default=False)


class AppReport(ReportBase):
    """A model for reporting apps."""

    app = ForeignKeyField(App, backref="reports")


class ScriptReport(ReportBase):
    """A model for reporting scripts."""

    script = ForeignKeyField(Script, backref="reports")
