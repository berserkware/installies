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


class CommentJunction(BaseModel):
    """A junction model between Comments and commentable things."""

    def get_all(self):
        """Gets the comments."""
        return self.comments

    def delete_instance(self):
        """Deletes the comments."""
        for comment in self.comments:
            comment.delete_instance()

        super().delete_instance()


class Thread(BaseModel):
    """A model for discussion threads."""

    title = CharField(255, unique=True)
    app = ForeignKeyField(App, backref='threads')
    comments = ForeignKeyField(CommentJunction, backref="threads")
    creator = ForeignKeyField(User, backref='threads')
    creation_date = DateTimeField(default=datetime.now)

    @classmethod
    def create(cls, **kwargs):
        """Creates the model."""
        group = CommentJunction.create()
        return super().create(comments=group, **kwargs)

    def delete_instance(self):
        super().delete_instance()

        self.comments.delete_instance()



class Comment(BaseModel):
    """A model for comments in dicussions."""

    group = ForeignKeyField(CommentJunction, backref='comments')
    creator = ForeignKeyField(User, backref='comments')
    creation_date = DateTimeField(default=datetime.now)
    content = TextField()
    edited = BooleanField(default=False)
