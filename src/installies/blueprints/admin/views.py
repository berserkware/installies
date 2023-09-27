from flask import Blueprint, flash, redirect, g
from installies.models.user import User
from installies.models.app import App
from installies.models.script import Script
from installies.models.discussion import Thread, Comment
from installies.lib.view import (
    AuthenticationRequiredMixin,
    TemplateView,
)

class AdminRequiredMixin:
    """A mixin for only allowing access to admins."""

    def on_request(self, **kwargs):
        if g.user.admin is False:
            flash('You must be admin to access this page.', 'error')
            return redirect('/')

        return super().on_request(**kwargs)


class AdminOptions(AuthenticationRequiredMixin, AdminRequiredMixin, TemplateView):
    """A view for displaying admin options."""

    template_path = 'admin/options.html'

    def get_context_data(self, **kwargs):
        kwargs['user_count'] = User.select().count()
        kwargs['app_count'] = App.select().count()
        kwargs['script_count'] = Script.select().count()
        kwargs['thread_count'] = Thread.select().count()
        kwargs['comment_count'] = Comment.select().count()
        
        return kwargs
