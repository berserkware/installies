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
)
from installies.validators.base import ValidationError
from installies.validators.app import (
    AppNameValidator,
    AppDescriptionValidator,
)
from installies.models.app import App
from installies.models.maintainer import Maintainer, Maintainers
from installies.models.user import User
from installies.forms.app import (
    CreateAppForm,
    EditAppForm,
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


class AppMixin:
    """
    A mixin for getting apclass="link-button"ps by url params.

    It gets the app slug from the app_slug kwarg.
    """
    
    maintainer_only = False
    
    def on_request(self, **kwargs):
        app_name = kwargs.get('app_name')

        if app_name is None:
            abort(404)

        app = App.select().where(App.name == app_name)

        if app.exists() is False:
            abort(404)

        app = app.get()

        if app.can_user_edit(g.user) is False and self.maintainer_only:
            flash(
                'You do not have permission to do that.',
                'error'
            )
            return redirect(url_for('app_manager.app_view', app_name=app.name), 303)

        kwargs['app'] = app
        
        return super().on_request(**kwargs)


    def get_app_view_redirect(self, **kwargs):
        """Get the redirect to the app view page."""
        app = kwargs['app']
        return redirect(url_for('app_manager.app_view', app_name=app.name), 303)


class CreateAppFormView(AuthenticationRequiredMixin, FormView):
    """A view for creating an app."""

    template_path = 'create_app.html'
    form_class = CreateAppForm

    def form_valid(self, form, **kwargs):
         app = form.save()

         flash('App successfully created.', 'success')
         return redirect(url_for('app_manager.app_view', app_name=app.name), 303)


class AppDetailView(AppMixin, TemplateView):
    """A view to get an app."""

    template_path = 'app/info.html'


class AppEditView(AuthenticationRequiredMixin, AppMixin, FormView):
    """A view to edit apps."""

    template_path = 'app/edit.html'
    form_class = EditAppForm
    maintainer_only = True

    def form_valid(self, form, **kwargs):
        form.save(kwargs['app'])
        
        flash('App succesfully edited.', 'success')
        return self.get_app_view_redirect(**kwargs)


class AppDeleteView(AdminRequiredMixin, AuthenticationRequiredMixin, AppMixin, TemplateView):
    """A view for deleting apps."""

    template_path = 'app/delete.html'

    def post(self, **kwargs):
        kwargs['app'].delete_instance()

        flash('App successfully deleted.', 'success')
        return redirect('/')
    

class AddMaintainerView(AuthenticationRequiredMixin, AppMixin, TemplateView):
    """A view for adding maintainers."""

    template_path = 'app/add_maintainer.html'
    maintainer_only = True

    def post(self, **kwargs):
        username = request.form.get('username').strip()

        user = User.select().where(User.username == username)

        if user.exists() is False:
            flash(f'{username} is not a user.', 'error')
            return self.get(**kwargs)

        user = user.get()
        app = kwargs['app']
        
        if app.maintainers.is_maintainer(user):
            flash(f'{user.username} is already a maintainer.', 'error')
            return redirect(url_for('app_manager.add_maintainer', app_name=app.name), 303)

        maintainer = app.maintainers.add_maintainer(user)

        flash(f'{user.username} successfully added as a maintainer.', 'success')
        return self.get_app_view_redirect(**kwargs)
        

class RemoveMaintainerView(AuthenticationRequiredMixin, AppMixin, TemplateView):
    """A view for removing a maintainer."""

    template_path = 'app/remove_maintainer.html'
    maintainer_only = True

    def on_request(self, **kwargs):
        user = User.select().where(User.username == kwargs['username'])

        if user.exists() is False:
            abort(404)

        user = user.get()

        kwargs['user'] = user

        return super().on_request(**kwargs)
    
    def post(self, **kwargs):
        app = kwargs['app']

        if len(app.maintainers.get_maintainers()) == 1:
            flash(f'You cannot remove the last maintainer.', 'error')
            return self.get_app_view_redirect(**kwargs)

        if app.maintainers.is_maintainer(kwargs['user']) is False:
            abort(404)
            
        app.maintainers.delete_maintainer(kwargs['user'])
        
        flash(f'Maintainer successfully removed.', 'success')
        return self.get_app_view_redirect(**kwargs)
