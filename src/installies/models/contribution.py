from installies.models.base import BaseModel
from installies.models.user import User
from installies.models.app import App
from peewee import (
    CharField,
    TextField,
    BooleanField,
    ForiegnKeyField,
)

class AppEditContribution(BaseModel):
    """A model for app edit contributions."""

    original_app = ForeignKeyField(App, backref='contributions')
    outdated = BooleanField(default=True)
    creator = ForiegnKeyField(User, backref='contributions')

    display_name = CharField(255, null=True)
    description = TextField(255, null=True)
    current_version = CharField(255, null=True)
    version_regex = CharField(255, null=True)
