from flask import Blueprint, render_template, request, flash, redirect, url_for, g, abort
from installies.models.report import Report, ReportAppInfo, ReportScriptInfo
from installies.validators.base import ValidationError
from installies.lib.view import (
    FormView,
    AuthenticationRequiredMixin,
    TemplateView,
    ListView,
    EditFormView,
)
from installies.blueprints.admin.views import AdminRequiredMixin


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

    template_path = 'report/detail.html'
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

    template_path = 'report/delete.html'
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
    
    template_path = 'report/resolve.html'
    public_only = True

    def post(self, **kwargs):
        report = kwargs['report']
        report.resolved = True
        report.save()
        flash('Report successfully resolved.', 'success')
        return redirect(url_for('admin.admin_options'), 303)


class ReportListView(AuthenticationRequiredMixin, AdminRequiredMixin, ListView):
    """A view for listing app reports."""

    template_path = 'report/list.html'
    public_only = True
    group_name = 'reports'

    def get_group(self, **kwargs):
        return Report.select()
