from flask import g
from installies.lib.form import Form, FormInput
from installies.validators.discussion import (
    ThreadTitleValidator,
    CommentContentValidator,
)
from installies.models.app import App
from installies.models.script import Script
from installies.models.discussion import Thread, Comment, CommentJunction


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

    def save(self, group: CommentJunction):
        return Comment.create(
            group=group,
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
