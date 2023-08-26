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
from installies.validators.script import (
    ScriptActionValidator,
    ScriptDistroValidator,
    ScriptContentValidator,
)
from installies.groups.script import ScriptGroup
from installies.models.app import App
from installies.models.maintainer import Maintainer, Maintainers
from installies.models.script import Script
from installies.models.user import User
from installies.forms.script import (
    AddScriptForm,
    EditScriptForm,
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


class ScriptMixin:
    """
    A mixin to get scripts by url params.

    Its gets the script's id from the script_id kwarg.
    """

    script_maintainer_only = False

    def on_request(self, **kwargs):
        script_id = kwargs['script_id']

        script = Script.select().where(Script.id == script_id)

        if script.exists() is False:
            abort(404)

        script = script.get()

        if kwargs['app'] != script.app:
            abort(404)
        
        if script.can_user_edit(g.user) is False and self.script_maintainer_only:
            flash(
                'You do not have permission to do that.',
                'error'
            )
            return redirect(url_for('app_manager.app_scripts', app_name=app.name), 303)

        kwargs['script'] = script

        return super().on_request(**kwargs)

    def get_script_view_redirect(self, **kwargs):
        """Gets the redirect to the script view page."""
        script = kwargs['script']
        return redirect(
            url_for('app_manager.script_view', app_name=kwargs['app'].name, script_id=script.id),
            303
        )

class ScriptListView(AppMixin, ListView):
    """A view for listing scripts"""

    template_path = 'script/app_scripts.html'
    group_name = 'scripts'
    paginator = Paginate(
        default_per_page = 10,
        max_per_page = 50,
    )

    def get_group(self, **kwargs):
        app_scripts = Script.select().where(Script.app == kwargs['app'])
        group = ScriptGroup.get(**request.args) & app_scripts
        return group

class ScriptDetailView(AppMixin, ScriptMixin, DetailView):
    """A view for getting the details of a script."""

    template_path = 'script/info.html'
    model_name = 'script'

    def get_object(self, **kwargs):
        return kwargs['script']


class ScriptDownloadView(AppMixin, ScriptMixin, View):
    """A view for getting the content of scripts."""

    def get(self, **kwargs):
        script = kwargs['script']
        content = script.complete_content(request.args.get('version'))
        script_file = io.BytesIO(content.encode('utf-8'))
        return send_file(
            script_file,
            mimetype='application/x-shellscript',
            download_name=f'{script.app.name}.sh',
            as_attachment=True
        )
    

class AddScriptFormView(AuthenticationRequiredMixin, AppMixin, FormView):
    """A view for adding apps."""

    template_path = 'script/add_script.html'
    form_class = AddScriptForm

    def form_valid(self, form, **kwargs):
        
        script = form.save(app=kwargs['app'])
        
        flash('Script successfully created.', 'success')
        return redirect(
            url_for('app_manager.script_view', app_name=kwargs['app'].name, script_id=script.id),
            303
        )


class EditScriptFormView(AuthenticationRequiredMixin, AppMixin, ScriptMixin, EditFormView):
    """A view for editing scripts."""

    template_path = 'script/edit_script.html'
    script_maintainer_only = True
    form_class = EditScriptForm

    def get_object_to_edit(self, **kwargs):
        return kwargs['script']
    
    def form_valid(self, form, **kwargs):
        print('valid')
        
        form.save(script=kwargs['script'])

        flash('Script successfully edited.', 'success')
        return self.get_app_view_redirect(**kwargs)


class DeleteScriptView(AuthenticationRequiredMixin, AppMixin, ScriptMixin, TemplateView):
    """A view for deleting scripts."""

    template_path = 'script/delete_script.html'
    script_maintainer_only = True

    def post(self, **kwargs):
        script = kwargs['script']
        script.delete_instance()
        flash('Script successfully deleted.', 'success')
        return self.get_app_view_redirect(**kwargs)


class AddScriptMaintainerView(AuthenticationRequiredMixin, AppMixin, ScriptMixin, TemplateView):
    """A view for adding maintainers to scripts."""

    template_path = 'script/add_maintainer.html'
    script_maintainer_only = True

    def post(self, **kwargs):
        username = request.form.get('username').strip()

        user = User.select().where(User.username == username)

        if user.exists() is False:
            flash(f'{username} is not a user.', 'error')
            return self.get(**kwargs)

        user = user.get()
        script = kwargs['script']
        
        if script.maintainers.is_maintainer(user):
            flash(f'{user.username} is already a maintainer.', 'error')
            return redirect(
                url_for(
                    'app_manager.add_script_maintainer',
                    app_name=app.name,
                    script_id=script.id,
                ),
                303
            )

        maintainer = script.maintainers.add_maintainer(user)

        flash(f'{user.username} successfully added as a maintainer.', 'success')
        return self.get_script_view_redirect(**kwargs)


class RemoveScriptMaintainerView(AuthenticationRequiredMixin, AppMixin, ScriptMixin, TemplateView):
    """A view for removing a maintainer."""

    template_path = 'script/remove_maintainer.html'
    maintainer_only = True

    def on_request(self, **kwargs):
        user = User.select().where(User.username == kwargs['username'])

        if user.exists() is False:
            abort(404)

        user = user.get()

        kwargs['user'] = user

        return super().on_request(**kwargs)
    
    def post(self, **kwargs):
        script = kwargs['script']

        if len(script.maintainers.get_maintainers()) == 1:
            flash(f'You cannot remove the last maintainer.', 'error')
            return self.get_script_view_redirect(**kwargs)

        if script.maintainers.is_maintainer(kwargs['user']) is False:
            abort(404)
            
        script.maintainers.delete_maintainer(kwargs['user'])
        
        flash(f'Maintainer successfully removed.', 'success')
        return self.get_script_view_redirect(**kwargs)
