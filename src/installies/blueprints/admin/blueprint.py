from flask import Blueprint
from installies.blueprints.admin.views import (
    AdminOptions,
)
from installies.blueprints.admin.report import (
    DeleteReportView,
    ReportDetailView,
    ResolveReportView,
    ReportListView,
)
from installies.blueprints.admin.ban import (
    BanUserFormView,
    UnbanUserFormView,
)

admin = Blueprint('admin', __name__)

admin.add_url_rule('/admin', 'admin_options', AdminOptions.as_view())

admin.add_url_rule('/admin/reports/<int:report_id>/delete', 'delete_report', DeleteReportView.as_view(), methods=['GET', 'POST'])
admin.add_url_rule('/admin/reports/<int:report_id>', 'report_view', ReportDetailView.as_view())
admin.add_url_rule('/admin/reports/<int:report_id>/resolve', 'resolve_report', ResolveReportView.as_view(), methods=['GET', 'POST'])
admin.add_url_rule('/admin/reports', 'reports', ReportListView.as_view())

admin.add_url_rule('/profile/<username>/ban', 'ban_user', BanUserFormView.as_view(), methods=['get', 'post'])
admin.add_url_rule('/profile/<username>/unban', 'unban_user', UnbanUserFormView.as_view(), methods=['get', 'post'])
