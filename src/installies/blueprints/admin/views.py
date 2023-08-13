from flask import Blueprint, render_template, request, flash, redirect, url_for, g, abort
from installies.models.report import ReportBase, AppReport, ScriptReport
from installies.models.user import User
from installies.validators.base import ValidationError
from installies.lib.view import FormView, AuthenticationRequiredMixin, TemplateView, ListView
from installies.blueprints.admin.form import (
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


class ReportMixin:
    """
    A mixin for getting reports.

    :param report_class: The class of the report. Default is the Report class.
    """

    report_class = ReportBase

    def on_request(self, **kwargs):
        report = self.report_class.select().where(self.report_class.id == kwargs['report_id'])

        if report.exists() is False:
            abort(404)

        report = report.get()

        kwargs['report'] = report
        
        return super().on_request(**kwargs)


class AppReportDetailView(
        AuthenticationRequiredMixin,
        AdminRequiredMixin,
        ReportMixin,
        TemplateView
):
    """A view to get app reports."""

    template_path = 'admin/app_report_view.html'
    public_only = True
    report_class = AppReport


class DeleteAppReportView(
        AuthenticationRequiredMixin,
        AdminRequiredMixin,
        ReportMixin,
        TemplateView
):
    """A view for deleting app reports."""

    template_path = 'admin/delete_app_report.html'
    public_only = True
    report_class = AppReport
    
    def post(self, **kwargs):
        report = kwargs['report']
        report.delete_instance()
        flash('Report successfully removed.', 'success')
        return redirect(url_for('admin.admin_options'), 303)


class ResolveAppReportView(
        AuthenticationRequiredMixin,
        AdminRequiredMixin,
        ReportMixin,
        TemplateView
):
    """A view for resolving app reports."""
    
    template_path = 'admin/resolve_app_report.html'
    public_only = True
    report_class = AppReport

    def post(self, **kwargs):
        report = kwargs['report']
        report.resolved = True
        report.save()
        flash('Report successfully resolved.', 'success')
        return redirect(url_for('admin.admin_options'), 303)


class AppReportListView(AuthenticationRequiredMixin, AdminRequiredMixin, ListView):
    """A view for listing app reports."""

    template_path = 'admin/app_reports.html'
    public_only = True
    group_name = 'reports'

    def get_group(self, **kwargs):
        return AppReport.select()



class ScriptReportDetailView(
        AuthenticationRequiredMixin,
        AdminRequiredMixin,
        ReportMixin,
        TemplateView
):
    """A view to get script reports."""

    template_path = 'admin/script_report_view.html'
    public_only = True
    report_class = ScriptReport


class DeleteScriptReportView(
        AuthenticationRequiredMixin,
        AdminRequiredMixin,
        ReportMixin,
        TemplateView
):
    """A view for deleting script reports."""

    template_path = 'admin/delete_script_report.html'
    public_only = True
    report_class = ScriptReport
    
    def post(self, **kwargs):
        report = kwargs['report']
        report.delete_instance()
        flash('Report successfully removed.', 'success')
        return redirect(url_for('admin.admin_options'), 303)


class ResolveScriptReportView(
        AuthenticationRequiredMixin,
        AdminRequiredMixin,
        ReportMixin,
        TemplateView
):
    """A view for resolving script reports."""
    
    template_path = 'admin/resolve_script_report.html'
    public_only = True
    report_class = ScriptReport

    def post(self, **kwargs):
        report = kwargs['report']
        report.resolved = True
        report.save()
        flash('Report successfully resolved.', 'success')
        return redirect(url_for('admin.admin_options'), 303)


class ScriptReportListView(AuthenticationRequiredMixin, AdminRequiredMixin, ListView):
    """A view for listing script reports."""

    template_path = 'admin/script_reports.html'
    public_only = True
    group_name = 'reports'

    def get_group(self, **kwargs):
        return ScriptReport.select()


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

admin.add_url_rule('/admin/app-reports/<int:report_id>/delete', 'delete_app_report', DeleteAppReportView.as_view(), methods=['GET', 'POST'])
admin.add_url_rule('/admin/app-reports/<int:report_id>', 'app_report_view', AppReportDetailView.as_view())
admin.add_url_rule('/admin/app-reports/<int:report_id>/resolve', 'resolve_app_report', ResolveAppReportView.as_view(), methods=['GET', 'POST'])
admin.add_url_rule('/admin/app-reports', 'app_reports', AppReportListView.as_view())

admin.add_url_rule('/admin/script-reports/<int:report_id>/delete', 'delete_script_report', DeleteScriptReportView.as_view(), methods=['GET', 'POST'])
admin.add_url_rule('/admin/script-reports/<int:report_id>', 'script_report_view', ScriptReportDetailView.as_view())
admin.add_url_rule('/admin/script-reports/<int:report_id>/resolve', 'resolve_script_report', ResolveScriptReportView.as_view(), methods=['GET', 'POST'])
admin.add_url_rule('/admin/script-reports', 'script_reports', ScriptReportListView.as_view())

admin.add_url_rule('/profile/<username>/ban', 'ban_user', BanUserFormView.as_view(), methods=['get', 'post'])
admin.add_url_rule('/profile/<username>/unban', 'unban_user', UnbanUserFormView.as_view(), methods=['get', 'post'])

