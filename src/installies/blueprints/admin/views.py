from flask import Blueprint, render_template, request, flash, redirect, url_for, g, abort
from installies.models.supported_distros import Distro
from installies.models.report import ReportBase, AppReport, ScriptReport
from installies.lib.validate import ValidationError
from installies.blueprints.admin.validate import DistroSlugValidator, DistroNameValidatior
from installies.lib.view import FormView, AuthenticationRequiredMixin, TemplateView, ListView
from installies.blueprints.admin.form import CreateDistroForm, CreateArchitectureForm

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

    
class AddDistroView(AuthenticationRequiredMixin, AdminRequiredMixin, FormView):
    """A view for adding distros."""

    template_path = 'admin/add_distro.html'
    form_class = CreateDistroForm

    def form_valid(self, form, **kwargs):
        based_on = form.data['distro-based-on']
        based_on_distro = None
        if based_on is not None and based_on != '':
            
            # checks that there is a distro that exists with the based on slug
            based_on_distro = Distro.select().where(Distro.slug == based_on)
            if based_on_distro.exists() is False:
                flash(f'Could not find distro to be based with the slug "{based_on}"', 'error')
                return redirect(url_for('admin.add_distro'))

            based_on_distro = based_on_distro.get()

        distro = form.save(based_on=based_on_distro)

        flash('Distro successfully created.', 'success')
        return redirect(url_for('admin.admin_options'))


class AddArchitectureView(AuthenticationRequiredMixin, AdminRequiredMixin, FormView):
    """A view for adding architechture."""

    template_path = 'admin/add_architecture.html'
    form_class = CreateArchitectureForm

    def form_valid(self, form, **kwarg):
        form.save()         

        flash('Architecture successfully created.', 'success')
        return redirect(url_for('admin.admin_options'))
        

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
    
    
admin.add_url_rule('/admin', 'admin_options', AdminOptions.as_view())    
admin.add_url_rule('/admin/add-distro', 'add_distro', AddDistroView.as_view(), methods=['get', 'post'])
admin.add_url_rule('/admin/add-architecture', 'add_architecture', AddArchitectureView.as_view(), methods=['get', 'post'])

admin.add_url_rule('/admin/app-reports/<int:report_id>/delete', 'delete_app_report', DeleteAppReportView.as_view(), methods=['GET', 'POST'])
admin.add_url_rule('/admin/app-reports/<int:report_id>', 'app_report_view', AppReportDetailView.as_view())
admin.add_url_rule('/admin/app-reports/<int:report_id>/resolve', 'resolve_app_report', ResolveAppReportView.as_view(), methods=['GET', 'POST'])
admin.add_url_rule('/admin/app-reports', 'app_reports', AppReportListView.as_view())

admin.add_url_rule('/admin/script-reports/<int:report_id>/delete', 'delete_script_report', DeleteScriptReportView.as_view(), methods=['GET', 'POST'])
admin.add_url_rule('/admin/script-reports/<int:report_id>', 'script_report_view', ScriptReportDetailView.as_view())
admin.add_url_rule('/admin/script-reports/<int:report_id>/resolve', 'resolve_script_report', ResolveScriptReportView.as_view(), methods=['GET', 'POST'])
admin.add_url_rule('/admin/script-reports', 'script_reports', ScriptReportListView.as_view())
