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

    title = CharField(255)
    creator = ForeignKeyField(User, backref='threads', null=True)
    creation_date = DateTimeField(default=datetime.now)

    def delete_instance(self):
        if self.app_data.exists():
            self.app_data.get().delete_instance()
        
        for comment in self.comments:
            comment.delete_instance()
        
        super().delete_instance()


    def can_user_edit(self, user: User):
        """Check if the given user is allowed to edit the thread."""
        if user is None:
            return False

        if user.admin is True:
            return True

        if user == self.creator:
            return True

        return False


class AppThread(BaseModel):
    """A model for app discussion threads."""

    thread = ForeignKeyField(Thread, backref='app_data')
    app = ForeignKeyField(App, backref='threads')


class Comment(BaseModel):
    """A model for comments in dicussions."""

    thread = ForeignKeyField(Thread, backref='comments')
    creator = ForeignKeyField(User, backref='comments')
    creation_date = DateTimeField(default=datetime.now)
    content = TextField()
    edited = BooleanField(default=False)

    def can_user_edit(self, user: User):
        """Check if the given user is allowed to edit the comment."""
        if user is None:
            return False

        if user.admin is True:
            return True

        if user == self.creator:
            return True

        return False
