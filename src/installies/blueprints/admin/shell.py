from flask import Blueprint, render_template, request, flash, redirect, url_for, g, abort
from installies.models.script import Script, Shell
from installies.validators.base import ValidationError
from installies.lib.view import (
    FormView,
    AuthenticationRequiredMixin,
    TemplateView,
    ListView,
    EditFormView,
)
from installies.forms.admin import (
    CreateShellForm,
    EditShellForm,
)
from installies.blueprints.admin.views import AdminRequiredMixin


class CreateShellFormView(AuthenticationRequiredMixin, AdminRequiredMixin, FormView):
    """A view for creating shells."""

    template_path = 'shell/create.html'
    form_class = CreateShellForm
    
    def form_valid(self, form, **kwargs):
        form.save()

        flash('Shell successfully created.', 'success')
        return redirect(url_for('admin.shells'))


class ShellMixin:
    """A mixin for getting shells from an shell_id in the URL."""

    def on_request(self, **kwargs):
        shell = Shell.select().where(Shell.id == kwargs['shell_id'])

        if shell.exists() is False:
            abort(404)

        shell = shell.get()

        kwargs['shell'] = shell
        
        return super().on_request(**kwargs)
    

class EditShellFormView(AuthenticationRequiredMixin, AdminRequiredMixin, ShellMixin, EditFormView):
    """A view for editing scripts."""

    template_path = 'shell/edit.html'
    form_class = EditShellForm

    def get_object_to_edit(self, **kwargs):
        return kwargs['shell']
    
    def form_valid(self, form, **kwargs):
        form.save(kwargs['shell'])

        flash('Shell successfully edited.', 'success')
        return redirect(url_for('admin.shells'))


class DeleteShellView(AuthenticationRequiredMixin, AdminRequiredMixin, ShellMixin, TemplateView):
    """A view for deleting shells."""

    template_path = 'shell/delete.html'

    def post(self, **kwargs):
        shell = kwargs['shell']
        shell.delete_instance()
        flash('Shell successfully deleted.', 'success')
        return redirect(url_for('admin.shells'))


class ShellListView(AuthenticationRequiredMixin, AdminRequiredMixin, ListView):
    """A view for listing shells."""

    template_path = 'shell/list.html'
    public_only = True
    group_name = 'shells'

    def get_group(self, **kwargs):
        return Shell.select()
