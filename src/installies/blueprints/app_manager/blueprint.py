from flask import Blueprint
from installies.blueprints.app_manager.app import (
    CreateAppFormView,
    AppDetailView,
    AppEditView,
    AddMaintainerView,
    AddMaintainerView,
    RemoveMaintainerView,
)
from installies.blueprints.app_manager.script import (
    ScriptListView,
    ScriptDetailView,
    ScriptDownloadView,
    AddScriptFormView,
    EditScriptFormView,
    DeleteScriptView,
    AddScriptMaintainerView,
    RemoveScriptMaintainerView,
    CreateScriptCommentView,
    EditScriptCommentView,
    DeleteScriptCommentView,
)
from installies.blueprints.app_manager.report import (
    ReportAppView,
    ReportScriptView,
)
from installies.blueprints.app_manager.discussion import (
    CreateThreadView,
    CreateCommentView,
    EditCommentView,
    DeleteCommentView,
    ThreadListView,
    CommentListView,
    DeleteThreadView,
)

app_manager = Blueprint('app_manager', __name__)

app_manager.add_url_rule('/create-app', 'create_app', CreateAppFormView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>', 'app_view', AppDetailView.as_view())
app_manager.add_url_rule('/apps/<app_name>/edit', 'app_edit', AppEditView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>/add-mantainer', 'add_maintainer', AddMaintainerView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>/maintainer/<username>/remove', 'remove_maintainer', RemoveMaintainerView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>/report', 'report_app', ReportAppView.as_view(), methods=['GET', 'POST'])

app_manager.add_url_rule('/apps/<app_name>/scripts', 'app_scripts', ScriptListView.as_view())
app_manager.add_url_rule('/apps/<app_name>/scripts/<int:script_id>', 'script_view', ScriptDetailView.as_view())
app_manager.add_url_rule('/apps/<app_name>/scripts/<int:script_id>/download', 'script_download', ScriptDownloadView.as_view())
app_manager.add_url_rule('/apps/<app_name>/add-script', 'add_script', AddScriptFormView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>/scripts/<int:script_id>/edit', 'edit_script', EditScriptFormView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>/scripts/<int:script_id>/delete', 'delete_script', DeleteScriptView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>/scripts/<int:script_id>/add-mantainer', 'add_script_maintainer', AddScriptMaintainerView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>/scripts/<int:script_id>/maintainer/<username>/remove', 'remove_script_maintainer', RemoveScriptMaintainerView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>/scripts/<int:script_id>/report', 'report_script', ReportScriptView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>/scripts/<int:script_id>/comment', 'create_script_comment', CreateScriptCommentView.as_view(), methods=['POST'])
app_manager.add_url_rule('/apps/<app_name>/scripts/<int:script_id>/comment/<int:comment_id>/edit', 'edit_script_comment', EditScriptCommentView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>/scripts/<int:script_id>/comment/<int:comment_id>/delete', 'delete_script_comment', DeleteScriptCommentView.as_view(), methods=['GET', 'POST'])

app_manager.add_url_rule('/apps/<app_name>/discussion/create-thread', 'create_thread', CreateThreadView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>/discussion/thread/<int:thread_id>/comment', 'create_comment', CreateCommentView.as_view(), methods=['POST'])
app_manager.add_url_rule('/apps/<app_name>/discussion/thread/<int:thread_id>/delete', 'delete_thread', DeleteThreadView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>/discussion/thread/<int:thread_id>/comment/<int:comment_id>/edit', 'edit_comment', EditCommentView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>/discussion/thread/<int:thread_id>/comment/<int:comment_id>/delete', 'delete_comment', DeleteCommentView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>/discussion', 'discussion', ThreadListView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>/discussion/thread/<int:thread_id>', 'comments', CommentListView.as_view(), methods=['GET', 'POST'])
