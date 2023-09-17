import bleach
import json
import os
import re
import math
import io

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    g,
    abort,
    flash,
    url_for,
    send_file,
)
from installies.validators.base import ValidationError
from installies.models.app import App
from installies.models.script import Script
from installies.models.user import User
from installies.models.discussion import Thread, Comment
from installies.forms.report import (
    ReportAppForm,
    ReportScriptForm,
)
from installies.forms.discussion import (
    CreateThreadForm,
    CreateCommentForm,
    EditCommentForm,
)
from installies.lib.view import (
    View,
    FormView,
    EditFormView,
    AuthenticationRequiredMixin,
    TemplateView,
    ListView,
    DetailView,
)
from peewee import JOIN
from installies.blueprints.admin.views import AdminRequiredMixin
from installies.groups.modifiers import Paginate
from installies.blueprints.app_manager.app import (
    AppMixin,
)


class CreateThreadView(AuthenticationRequiredMixin, AppMixin, FormView):
    """A view for creating discussion threads."""

    template_path = 'discussion/create_thread.html'
    form_class = CreateThreadForm

    def form_valid(self, form, **kwargs):
        thread = form.save(app=kwargs['app'])

        flash('Topic successfully created.', 'success')
        return redirect(
            url_for(
                'app_manager.comments',
                app_name=kwargs['app'].name,
                thread_id=thread.id
            ),
            303
        )


class ThreadMixin:
    """A mixin for getting threads from url variables."""

    # if this is true it will only allow admins and thread owners to
    # access
    modify_view = False
    
    def on_request(self, **kwargs):
        thread = Thread.select().where(Thread.id == kwargs['thread_id'])

        if thread.exists() is False:
            abort(404)

        thread = thread.get()

        if thread.app != kwargs['app']:
            abort(404)

        if self.modify_view and thread.can_user_edit(g.user) is False:
            flash('You do not have permission to modify this thread.', 'error')
            return redirect(
                url_for(
                    'app_manager.comments',
                    app_name=kwargs['app'].name,
                    thread_id=thread.id
                ),
                303
            )
            
        kwargs['thread'] = thread
        return super().on_request(**kwargs)


class DeleteThreadView(AuthenticationRequiredMixin, AppMixin, ThreadMixin, FormView):
    """A view for deleting threads."""

    template_path = 'discussion/delete_thread.html'
    modify_view = True

    def post(self, **kwargs):
        thread = kwargs['thread']

        thread.delete_instance()
        
        flash('Thread successfully deleted.', 'success')
        return self.get_app_view_redirect(**kwargs)
    

class CreateCommentView(AuthenticationRequiredMixin, AppMixin, ThreadMixin, FormView):
    """A view for creating comments"""

    form_class = CreateCommentForm

    def form_invaid(self, form, **kwargs):
        return redirect(
            url_for(
                'app_manager.comments',
                app_name=kwargs['app'].name,
                thread_id=kwargs['thread'].id
            ),
            303
        )
    
    def form_valid(self, form, **kwargs):
        form.save(thread=kwargs['thread'])

        flash('Comment successfully posted.', 'success')
        return redirect(
            url_for(
                'app_manager.comments',
                app_name=kwargs['app'].name,
                thread_id=kwargs['thread'].id
            ),
            303
        )


class CommentMixin:
    """A mixin for getting comments from url variables."""

    def on_request(self, **kwargs):
        comment = Comment.select().where(Comment.id == kwargs['comment_id'])

        if comment.exists() is False:
            abort(404)

        comment = comment.get()

        if comment.can_user_edit(g.user) is False:
            flash('You do not have permission to modify this comment.', 'error')
            return self.get_app_view_redirect(**kwargs)

        if comment.thread != kwargs['thread']:
            return abort(404)
        
        kwargs['comment'] = comment
        return super().on_request(**kwargs)
    

class EditCommentView(AuthenticationRequiredMixin, AppMixin, ThreadMixin, CommentMixin, EditFormView):
    """A view for editing comments."""

    template_path = 'discussion/edit_comment.html'
    form_class = EditCommentForm

    def get_object_to_edit(self, **kwargs):
        return kwargs['comment']
    
    def form_valid(self, form, **kwargs):
        form.save()

        flash('Comment successfully edited', 'success')
        return redirect(
            url_for(
                'app_manager.comments',
                app_name=kwargs['app'].name,
                thread_id=kwargs['thread'].id
            ),
            303
        )


class DeleteCommentView(AuthenticationRequiredMixin, AppMixin, ThreadMixin, CommentMixin, FormView):
    """A view for deleting comments."""

    template_path = 'discussion/delete_comment.html'

    def post(self, **kwargs):
        kwargs['comment'].delete_instance()

        flash('Comment successfully deleted', 'success')
        return redirect(
            url_for(
                'app_manager.comments',
                app_name=kwargs['app'].name,
                thread_id=kwargs['thread'].id
            ),
            303
        )


class CommentListView(AppMixin, ThreadMixin, ListView):
    """A view for listing comments."""

    template_path = 'discussion/comments.html'
    group_name = 'comments'
    paginator = Paginate(
        default_per_page = 10,
        max_per_page = 50,
    )

    def get_group(self, **kwargs):
        return kwargs['thread'].comments


class ThreadListView(AppMixin, ListView):
    """A view for listing threads."""

    template_path = 'discussion/threads.html'
    group_name = 'threads'
    paginator = Paginate(
        default_per_page = 10,
        max_per_page = 50,
    )

    def get_group(self, **kwargs):
        return Thread.select().where(Thread.app == kwargs['app'])
