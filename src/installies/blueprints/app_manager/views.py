import bleach
import json
import os
import re
import math

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    g,
    abort,
    flash,
    url_for
)
from installies.blueprints.app_manager.upload import (
    get_distros_from_string,
)
from installies.lib.validate import ValidationError
from installies.blueprints.app_manager.validate import (
    AppNameValidator,
    AppDescriptionValidator,
    AppVisibilityValidator,
    ScriptActionValidator,
    ScriptDistroValidator,
    ScriptContentValidator
)
from installies.groups.script import ScriptGroup
from installies.config import (
    supported_script_actions,
    supported_visibility_options,
)
from installies.models.app import App, Maintainer
from installies.models.script import Script
from installies.models.user import User
from installies.models.report import ReportBase, AppReport
from installies.models.discussion import Thread, Comment
from installies.blueprints.auth.decorators import authenticated_required
from installies.blueprints.app_manager.form import (
    CreateAppForm,
    EditAppForm,
    ChangeAppVisibilityForm,
    AddScriptForm,
    EditScriptForm,
    ReportAppForm,
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
from installies.database.modifiers import Paginate


class AppMixin:
    """
    A mixin for getting apps by url params.

    It gets the app slug from the app_slug kwarg.
    """

    public_only = False
    maintainer_only = False
    
    def on_request(self, **kwargs):
        app_name = kwargs.get('app_name')

        if app_name is None:
            abort(404)

        app = App.select().where(App.name == app_name)

        if app.exists() is False:
            abort(404)

        app = app.get()
        
        if self.public_only and app.visibility != 'public' and app.can_user_edit(g.user) is False:
            abort(404)

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

    template_path = 'app_view/info.html'
    public_only = True


class AppDeleteView(AuthenticationRequiredMixin, AppMixin, TemplateView):
    """A view to delete apps."""

    template_path = 'app_view/delete.html'
    public_only = True
    maintainer_only = True

    def post(self, **kwargs):
        app = kwargs['app']
        app.delete_instance()
        flash('App successfully deleted!', 'success')
        return redirect('/', 303)


class AppEditView(AuthenticationRequiredMixin, AppMixin, FormView):
    """A view to edit apps."""

    template_path = 'app_view/edit.html'
    form_class = EditAppForm
    public_only = True
    maintainer_only = True

    def form_valid(self, form, **kwargs):
        app = kwargs['app']
        form.save(app)
        flash('App succesfully edited.', 'success')
        return self.get_app_view_redirect(**kwargs)


class AppChangeVisibilityView(AuthenticationRequiredMixin, AppMixin, FormView):
    """A view to change visibility."""

    template_path = 'app_view/change_visibility.html'
    public_only = True
    maintainer_only = True
    form_class = ChangeAppVisibilityForm

    def form_valid(self, form, **kwargs):
        app = kwargs['app']
        # if app has no scripts, dont allow to make public
        if form.data['visibility'] != 'private' and len(app.scripts) == 0:
            flash('App must have at least one script to be made public', 'error')
            return self.get_app_view_redirect(**kwargs)

        form.save(app=app)

        flash(f'App visibility successfully changed to {form.data["visibility"]}.', 'success')
        return self.get_app_view_redirect(**kwargs)


class AddMaintainerView(AuthenticationRequiredMixin, AppMixin, TemplateView):
    """A view for adding maintainers."""

    template_path = 'app_view/add_maintainer.html'
    public_only = True
    maintainer_only = True

    def post(self, **kwargs):
        username = request.form.get('username').strip()

        user = User.select().where(User.username == username)

        if user.exists() is False:
            flash(f'{username} is not a user.', 'error')
            return self.get(**kwargs)

        user = user.get()
        
        if (Maintainer.select()
            .where(Maintainer.user == user)
            .where(Maintainer.app == app)
            .exists()):
            flash(f'{user.username} is already a maintainer.', 'error')
            return redirect(url_for('app_manager.add_maintainer', app_name=app.name), 303)

        maintainer = Maintainer.create(user=user, app=app)

        flash(f'{user.username} successfully added as a maintainer.', 'success')
        return self.get_app_view_redirect(**kwargs)
        

class RemoveMaintainerView(AuthenticationRequiredMixin, AppMixin, TemplateView):
    """A view for removing maintainer"""

    template_path = 'app_view/remove_maintainer.html'
    public_only = True
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
        
        maintainer = (
            Maintainer
            .select()
            .where(Maintainer.user == kwargs['user'])
            .where(Maintainer.app == app)
        )
        
        if maintainer.exists() is False:
            abort(404)

        maintainer = maintainer.get()

        if len(app.maintainers) == 1:
            flash(f'You cannot remove the last maintainer.', 'error')
            return self.get_app_view_redirect(**kwargs)
        
        maintainer.delete_instance()

        flash(f'Maintainer successfully removed.', 'success')
        return self.get_app_view_redirect(**kwargs)

class ScriptListView(AppMixin, ListView):
    """A view for listing scripts"""

    template_path = 'app_view/scripts.html'
    public_only = True
    group_name = 'scripts'
    paginator = Paginate(
        default_per_page = 10,
        max_per_page = 50,
    )

    def get_group(self, **kwargs):
        return ScriptGroup.get(**request.args).where(Script.app == kwargs['app'])


class ScriptDetailView(AppMixin, DetailView):
    """A view for getting the details of a script."""

    template_path = 'app_view/script_info.html'
    public_only = True
    model_name = 'script'

    def get_object(self, **kwargs):
        return Script.get_by_id(kwargs['script_id'])


class AddScriptFormView(AuthenticationRequiredMixin, AppMixin, FormView):
    """A view for adding apps."""

    template_path = 'app_view/add_script.html'
    public_only = True
    maintainer_only = True
    form_class = AddScriptForm

    def get_context_data(self, **kwargs):
        kwargs['possible_script_actions'] = supported_script_actions
        return kwargs

    def form_valid(self, form, **kwargs):
        if re.fullmatch(kwargs['app'].version_regex, form.data['for-version']) is None and form.data['for-version'] != '':
            flash('Version does not match app\'s version regex.', 'error')
            return self.get(**kwargs)
        
        form.save(app=kwargs['app'])
        
        flash('Script successfully created.', 'success')
        return self.get_app_view_redirect(**kwargs)


class EditScriptFormView(AuthenticationRequiredMixin, AppMixin, FormView):
    """A view for editing scripts."""

    template_path = 'app_view/edit_script.html'
    public_only = True
    maintainer_only = True
    form_class = EditScriptForm

    def on_request(self, **kwargs):
        kwargs['script'] = Script.get_by_id(kwargs['script_id'])
        return super().on_request(**kwargs)
    
    def get_context_data(self, **kwargs):
        kwargs['possible_script_actions'] = supported_script_actions
        return kwargs

    def form_valid(self, form, **kwargs):
        form.save(script=kwargs['script'])

        flash('Script successfully edited.', 'success')
        return self.get_app_view_redirect(**kwargs)


class DeleteScriptView(AuthenticationRequiredMixin, AppMixin, TemplateView):
    """A view for deleting scripts."""

    template_path = 'app_view/delete_script.html'
    public_only = True
    maintainer_only = True

    def on_request(self, **kwargs):
        kwargs['script'] = Script.get_by_id(kwargs['script_id'])
        return super().on_request(**kwargs)

    def post(self, **kwargs):
        script = kwargs['script']
        script.delete_instance()
        flash('Script successfully deleted.', 'success')
        return self.get_app_view_redirect(**kwargs)


class ReportAppView(AuthenticationRequiredMixin, AppMixin, FormView):
    """A view for reporting apps."""

    template_path = 'app_view/report_app.html'
    public_only = True
    form_class = ReportAppForm

    def form_valid(self, form, **kwargs):
        form.save(app=kwargs['app'])

        flash('App successfully reported.', 'success')
        return self.get_app_view_redirect(**kwargs)


class CreateThreadView(AuthenticationRequiredMixin, AppMixin, FormView):
    """A view for creating discussion threads."""

    template_path = 'app_view/create_thread.html'
    public_only = True
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

    template_path = 'app_view/delete_thread.html'
    public_only = True

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

    public_only = True
    form_class = CreateCommentForm
    
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

    template_path = 'app_view/edit_comment.html'
    public_only = True
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

    template_path = 'app_view/delete_comment.html'
    public_only = True

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

    template_path = 'app_view/comments.html'
    public_only = True
    group_name = 'comments'
    paginator = Paginate(
        default_per_page = 10,
        max_per_page = 50,
    )

    def get_group(self, **kwargs):
        return kwargs['thread'].comments


class ThreadListView(AppMixin, ListView):
    """A view for listing threads."""

    template_path = 'app_view/threads.html'
    public_only = True
    group_name = 'threads'
    paginator = Paginate(
        default_per_page = 10,
        max_per_page = 50,
    )

    def get_group(self, **kwargs):
        return Thread.select().where(Thread.app == kwargs['app'])
