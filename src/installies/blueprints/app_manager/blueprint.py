from flask import Blueprint
from installies.blueprints.app_manager.views import (
    CreateAppFormView,
    AppDetailView,
    AppDeleteView,
    AppEditView,
    AppChangeVisibilityView,
    AddMaintainerView,
    RemoveMaintainerView,
    ScriptListView,
    ScriptDetailView,
    AddScriptFormView,
    EditScriptFormView,
    DeleteScriptView,
    ReportAppView,
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
app_manager.add_url_rule('/apps/<app_name>/delete', 'app_delete', AppDeleteView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>/edit', 'app_edit', AppEditView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>/change-visibility', 'change_visibility', AppChangeVisibilityView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>/add-mantainer', 'add_maintainer', AddMaintainerView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>/maintainer/<username>/remove', 'remove_maintainer', RemoveMaintainerView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>/report', 'report_app', ReportAppView.as_view(), methods=['GET', 'POST'])

app_manager.add_url_rule('/apps/<app_name>/scripts', 'app_scripts', ScriptListView.as_view())
app_manager.add_url_rule('/apps/<app_name>/scripts/<int:script_id>', 'script_view', ScriptDetailView.as_view())
app_manager.add_url_rule('/apps/<app_name>/add-script', 'add_script', AddScriptFormView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>/scripts/<int:script_id>/edit', 'edit_script', EditScriptFormView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>/scripts/<int:script_id>/delete', 'delete_script', DeleteScriptView.as_view(), methods=['GET', 'POST'])

app_manager.add_url_rule('/apps/<app_name>/discussion/create-thread', 'create_thread', CreateThreadView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>/discussion/thread/<int:thread_id>/create-comment', 'create_comment', CreateCommentView.as_view(), methods=['POST'])
app_manager.add_url_rule('/apps/<app_name>/discussion/thread/<int:thread_id>/delete', 'delete_thread', DeleteThreadView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>/discussion/thread/<int:thread_id>/comment/<int:comment_id>/edit', 'edit_comment', EditCommentView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>/discussion/thread/<int:thread_id>/comment/<int:comment_id>/delete', 'delete_comment', DeleteCommentView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>/discussion', 'discussion', ThreadListView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_name>/discussion/thread/<int:thread_id>', 'comments', CommentListView.as_view(), methods=['GET', 'POST'])
