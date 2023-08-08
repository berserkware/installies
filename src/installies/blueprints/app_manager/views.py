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
from installies.blueprints.app_manager.upload import (
    get_distros_from_string,
)
from installies.lib.validate import ValidationError
from installies.blueprints.app_manager.validate import (
    AppNameValidator,
    AppDescriptionValidator,
    ScriptActionValidator,
    ScriptDistroValidator,
    ScriptContentValidator
)
from installies.groups.script import ScriptGroup
from installies.models.app import App
from installies.models.maintainer import Maintainer, Maintainers
from installies.models.script import Script
from installies.models.user import User
from installies.models.report import ReportBase, AppReport
from installies.models.discussion import Thread, Comment
from installies.blueprints.auth.decorators import authenticated_required
from installies.blueprints.app_manager.form import (
    CreateAppForm,
    EditAppForm,
    AddScriptForm,
    EditScriptForm,
    ReportAppForm,
    ReportScriptForm,
    CreateThreadForm,
    CreateCommentForm,
    EditCommentForm,
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


class AppDeleteView(AuthenticationRequiredMixin, AppMixin, TemplateView):
    """A view to delete apps."""

    template_path = 'app/delete.html'
    maintainer_only = True

    def post(self, **kwargs):
        app = kwargs['app']
        app.delete_instance()
        flash('App successfully deleted!', 'success')
        return redirect('/', 303)


class AppEditView(AuthenticationRequiredMixin, AppMixin, FormView):
    """A view to edit apps."""

    template_path = 'app/edit.html'
    form_class = EditAppForm
    maintainer_only = True

    def form_valid(self, form, **kwargs):
        app = kwargs['app']
        form.save(app)
        flash('App succesfully edited.', 'success')
        return self.get_app_view_redirect(**kwargs)


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
        return ScriptGroup.get(**request.args).where(Script.app == kwargs['app'])


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


class EditScriptFormView(AuthenticationRequiredMixin, AppMixin, ScriptMixin, FormView):
    """A view for editing scripts."""

    template_path = 'script/edit_script.html'
    script_maintainer_only = True
    form_class = EditScriptForm

    def form_valid(self, form, **kwargs):
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

    template_path = 'script/report_script.html'
    form_class = ReportScriptForm

    def form_valid(self, form, **kwargs):
        form.save(script=kwargs['script'])

        flash('Script successfully reported.', 'success')
        return self.get_script_view_redirect(**kwargs)


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

    def on_request(self, **kwargs):
        thread = Thread.select().where(Thread.id == kwargs['thread_id'])

        if thread.exists() is False:
            abort(404)

        kwargs['thread'] = thread.get()
        return super().on_request(**kwargs)


class DeleteThreadView(AuthenticationRequiredMixin, AppMixin, ThreadMixin, FormView):
    """A view for deleting threads."""

    template_path = 'discussion/delete_thread.html'

    def post(self, **kwargs):
        if kwargs['thread'].creator != g.user:
            flash('You do not have permission to delete this thread.', 'error')
            return redirect(
                url_for(
                    'app_manager.comments',
                    app_name=kwargs['app'].name,
                    thread_id=kwargs['thread'].id
                ),
                303
            )

        thread = kwargs['thread']

        for comment in thread.comments:
            comment.delete_instance()
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

        if comment.creator != g.user:
            flash('You do not have permission to modify this comment.', 'error')
            return self.get_app_view_redirect(**kwargs)
        
        kwargs['comment'] = comment
        return super().on_request(**kwargs)
    

class EditCommentView(AuthenticationRequiredMixin, AppMixin, ThreadMixin, CommentMixin, FormView):
    """A view for editing comments."""

    template_path = 'discussion/edit_comment.html'
    form_class = EditCommentForm
    
    def form_valid(self, form, **kwargs):
        form.save(comment=kwargs['comment'])

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
