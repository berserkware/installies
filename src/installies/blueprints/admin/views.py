from flask import Blueprint, render_template, request, flash, redirect, url_for, g, abort
from installies.models.report import Report, ReportAppInfo, ReportScriptInfo
from installies.models.user import User
from installies.models.app import App
from installies.models.script import Script
from installies.models.discussion import Thread, Comment
from installies.validators.base import ValidationError
from installies.lib.view import FormView, AuthenticationRequiredMixin, TemplateView, ListView
from installies.forms.admin import (
    BanUserForm,
)

admin = Blueprint('admin', __name__)

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

class ReportMixin:
    """
    A mixin for getting reports.

    :param report_class: The class of the report. Default is the Report class.
    """

    def on_request(self, **kwargs):
        report = Report.select().where(Report.id == kwargs['report_id'])

        if report.exists() is False:
            abort(404)

        report = report.get()

        kwargs['report'] = report
        
        return super().on_request(**kwargs)


class ReportDetailView(
        AuthenticationRequiredMixin,
        AdminRequiredMixin,
        ReportMixin,
        TemplateView
):
    """A view to get app reports."""

    template_path = 'admin/report_view.html'
    public_only = True

    def get(self, **kwargs):
        report = kwargs['report']

        if report.report_type == 'app':
            kwargs['app'] = report.app_data.get().app
        elif report.report_type == 'script':
            kwargs['script'] = report.script_data.get().script
        elif report.report_type == 'comment':
            kwargs['comment'] = report.comment_data.get().comment
        
        return super().get(**kwargs)

class DeleteReportView(
        AuthenticationRequiredMixin,
        AdminRequiredMixin,
        ReportMixin,
        TemplateView
):
    """A view for deleting app reports."""

    template_path = 'admin/delete_report.html'
    public_only = True
    
    def post(self, **kwargs):
        report = kwargs['report']
        report.delete_instance()
        flash('Report successfully removed.', 'success')
        return redirect(url_for('admin.admin_options'), 303)


class ResolveReportView(
        AuthenticationRequiredMixin,
        AdminRequiredMixin,
        ReportMixin,
        TemplateView
):
    """A view for resolving app reports."""
    
    template_path = 'admin/resolve_report.html'
    public_only = True

    def post(self, **kwargs):
        report = kwargs['report']
        report.resolved = True
        report.save()
        flash('Report successfully resolved.', 'success')
        return redirect(url_for('admin.admin_options'), 303)


class ReportListView(AuthenticationRequiredMixin, AdminRequiredMixin, ListView):
    """A view for listing app reports."""

    template_path = 'admin/reports.html'
    public_only = True
    group_name = 'reports'

    def get_group(self, **kwargs):
        return Report.select()


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
    
    
admin.add_url_rule('/admin', 'admin_options', AdminOptions.as_view())

admin.add_url_rule('/admin/reports/<int:report_id>/delete', 'delete_report', DeleteReportView.as_view(), methods=['GET', 'POST'])
admin.add_url_rule('/admin/reports/<int:report_id>', 'report_view', ReportDetailView.as_view())
admin.add_url_rule('/admin/reports/<int:report_id>/resolve', 'resolve_report', ResolveReportView.as_view(), methods=['GET', 'POST'])
admin.add_url_rule('/admin/reports', 'reports', ReportListView.as_view())

admin.add_url_rule('/profile/<username>/ban', 'ban_user', BanUserFormView.as_view(), methods=['get', 'post'])
admin.add_url_rule('/profile/<username>/unban', 'unban_user', UnbanUserFormView.as_view(), methods=['get', 'post'])

