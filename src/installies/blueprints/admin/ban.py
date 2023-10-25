from flask import Blueprint, render_template, request, flash, redirect, url_for, g, abort
from installies.models.user import User
from installies.validators.base import ValidationError
from installies.lib.view import (
    FormView,
    AuthenticationRequiredMixin,
    TemplateView,
    ListView,
)
from installies.forms.admin import BanUserForm
from installies.blueprints.admin.views import AdminRequiredMixin


class BanUserFormView(AuthenticationRequiredMixin, AdminRequiredMixin, FormView):
    """A view for banning users."""

    template_path = 'admin/ban_user.html'
    form_class = BanUserForm

    def on_request(self, **kwargs):
        user = User.select().where(User.username == kwargs['username'])

        if user.exists() is False:
            abort(404)

        user = user.get()

        if len(user.bans) > 0:
            flash('User already banned.', 'error')
            return redirect(url_for('app_library.index'))

        kwargs['user'] = user
        return super().on_request(**kwargs)
    
    def form_valid(self, form, **kwargs):
        form.save(user=kwargs['user'])

        for session in kwargs['user'].sessions:
            session.delete_instance()
        
        flash('User successfully banned.', 'success')
        return redirect(url_for('app_library.index'))


class UnbanUserFormView(AuthenticationRequiredMixin, AdminRequiredMixin, TemplateView):
    """A view for unbanning users."""

    template_path = 'admin/unban_user.html'

    def on_request(self, **kwargs):
        user = User.select().where(User.username == kwargs['username'])

        if user.exists() is False:
            abort(404)

        user = user.get()

        if len(user.bans) == 0:
            flash('User not banned.', 'error')
            return redirect(url_for('app_library.index'))
        
        kwargs['user'] = user
        return super().on_request(**kwargs)

    def post(self, **kwargs):
        user = kwargs['user']

        for ban in user.bans:
            ban.delete_instance()

        flash('User successfully unbanned.', 'success')
        return redirect(url_for('app_library.index'))
