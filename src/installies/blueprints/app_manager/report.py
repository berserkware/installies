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
from installies.forms.report import (
    ReportAppForm,
    ReportScriptForm,
    ReportCommentForm,
)
from installies.lib.view import (
    View,
    FormView,
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
from installies.blueprints.app_manager.script import (
    ScriptMixin,
)
from installies.blueprints.app_manager.discussion import CommentMixin, ThreadMixin


class ReportAppView(AuthenticationRequiredMixin, AppMixin, FormView):
    """A view for reporting apps."""

    template_path = 'app/report_app.html'
    form_class = ReportAppForm

    def form_valid(self, form, **kwargs):
        form.save(app=kwargs['app'])

        flash('App successfully reported.', 'success')
        return self.get_app_view_redirect(**kwargs)


class ReportScriptView(AuthenticationRequiredMixin, AppMixin, ScriptMixin, FormView):
    """A view for reporting scripts."""

    template_path = 'script/report.html'
    form_class = ReportScriptForm

    def form_valid(self, form, **kwargs):
        form.save(script=kwargs['script'])

        flash('Script successfully reported.', 'success')
        return self.get_script_view_redirect(**kwargs)


class ReportAppCommentView(AuthenticationRequiredMixin, AppMixin, ThreadMixin, CommentMixin, FormView):
    """A view for reporting comments."""

    template_path = 'discussion/report_comment.html'
    form_class = ReportCommentForm

    def form_valid(self, form, **kwargs):
        form.save(comment=kwargs['comment'])

        flash('Comment successfully reported.', 'success')
        return self.get_app_view_redirect(**kwargs)
