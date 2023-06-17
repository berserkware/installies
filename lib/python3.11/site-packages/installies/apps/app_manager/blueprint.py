from flask import Blueprint
from installies.apps.app_manager.views import (
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
)

app_manager = Blueprint('app_manager', __name__)

app_manager.add_url_rule('/create-app', 'create_app', CreateAppFormView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_slug>', 'app_view', AppDetailView.as_view())
app_manager.add_url_rule('/apps/<app_slug>/delete', 'app_delete', AppDeleteView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_slug>/edit', 'app_edit', AppEditView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_slug>/change-visibility', 'change_visibility', AppChangeVisibilityView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_slug>/add-mantainer', 'add_maintainer', AddMaintainerView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_slug>/maintainer/<username>/remove', 'remove_maintainer', RemoveMaintainerView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_slug>/scripts', 'app_scripts', ScriptListView.as_view())
app_manager.add_url_rule('/apps/<app_slug>/scripts/<int:script_id>', 'script_view', ScriptDetailView.as_view())
app_manager.add_url_rule('/apps/<app_slug>/add-script', 'add_script', AddScriptFormView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_slug>/scripts/<int:script_id>/edit', 'edit_script', EditScriptFormView.as_view(), methods=['GET', 'POST'])
app_manager.add_url_rule('/apps/<app_slug>/scripts/<int:script_id>/delete', 'delete_script', DeleteScriptView.as_view(), methods=['GET', 'POST'])
