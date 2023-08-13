from installies.models.base import BaseModel
from installies.models.user import User
from installies.models.app import App
from peewee import (
    CharField,
    ForeignKeyField,
    DateTimeField,
    TextField,
    BooleanField,
)
from datetime import datetime


class Thread(BaseModel):
    """A model for discussion threads."""

    title = CharField(255, unique=True)
    app = ForeignKeyField(App, backref='threads')
    creator = ForeignKeyField(User, backref='threads')
    creation_date = DateTimeField(default=datetime.now)

    def delete_instance(self):
        for comment in self.comments:
            comment.delete_instance()

        super().delete_instance()


class Comment(BaseModel):
    """A model for comments in dicussions."""

    thread = ForeignKeyField(Thread, backref='comments')
    creator = ForeignKeyField(User, backref='comments')
    creation_date = DateTimeField(default=datetime.now)
    content = TextField()
    edited = BooleanField(default=False)
