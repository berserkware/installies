from flask import g
from installies.forms.base import Form, FormInput
from installies.validators.discussion import (
    ThreadTitleValidator,
    CommentContentValidator,
)
from installies.models.app import App
from installies.models.script import Script
from installies.models.discussion import Thread, Comment


class CreateThreadForm(Form):
    """A form to create threads."""

    inputs = [
        FormInput('title', ThreadTitleValidator)
    ]
    
    model = Thread

    def save(self, app: App):
        return Thread.create(
            title=self.data['title'],
            creator=g.user,
            app=app,
        )


class CommentForm(Form):
    """A base form for creating or editing comments."""

    inputs = [
        FormInput('content', CommentContentValidator)
    ]

    model = Comment

    
class CreateCommentForm(CommentForm):
    """A form to create comments."""

    def save(self, thread: Thread):
        return Comment.create(
            thread=thread,
            creator=g.user,
            content=self.data['content'],
        )


class EditCommentForm(CommentForm):
    """A form to edit comments"""

    edit_form = True

    def save(self, comment: Comment):
        comment.content = self.data['content']
        comment.edited = True
        comment.save()
        return comment
