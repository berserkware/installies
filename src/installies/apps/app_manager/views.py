import bleach
import json
import os

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    g,
    abort,
    flash,
    url_for
)
from installies.apps.app_manager.upload import (
    get_distros_from_string,
)
from installies.lib.validate import ValidationError
from installies.apps.app_manager.validate import (
    AppNameValidator,
    AppDescriptionValidator,
    AppVisibilityValidator,
    ScriptActionValidator,
    ScriptDistroValidator,
    ScriptContentValidator
)
from installies.config import (
    supported_script_actions,
    supported_visibility_options,
)
from installies.apps.app_manager.models import App, Script
from installies.apps.auth.decorators import authenticated_required
from peewee import JOIN

app_manager = Blueprint('app_manager', __name__)

@app_manager.route('/create-app', methods=['GET', 'POST'])
@authenticated_required()
def create_app():
    if request.method == 'POST':
        app_name = request.form.get('app-name', '').strip()
        app_description = request.form.get('app-desc', '').strip()

        # returns error to user if app name is not clean
        try:
            AppNameValidator.validate(app_name)
            AppDescriptionValidator.validate(app_description)
        except ValidationError as e:
            flash(str(e), 'error')
            return redirect(url_for('app_manager.create_app'), 303)

        app = App.create(app_name, app_description, g.user)

        flash('App successfully created.', 'success')
        return redirect(url_for('app_manager.app_view', slug=app.slug), 303)

    return render_template('create_app.html')


@app_manager.route('/apps/<slug>', methods=['GET', 'POST'])
def app_view(slug):
    app = App.get_by_slug(slug)
    
    return render_template('app_view/info.html', app=app)


@app_manager.route('/apps/<slug>/delete', methods=['GET', 'POST'])
@authenticated_required()
def app_delete(slug):
    app = App.get_by_slug(slug)
    
    if app.submitter != g.user:
        flash(
            'You cannot delete an app that you are not the submitter of.',
            'error'
        )
        return redirect(url_for('app_manager.app_view', slug=app.slug), 303)

    if request.method == 'POST':
        app.delete_instance()
        flash('App successfully deleted!', 'success')
        return redirect('/', 303)

    return render_template('app_view/delete.html', app=app)


@app_manager.route('/apps/<slug>/edit', methods=['GET', 'POST'])
@authenticated_required()
def app_edit(slug):
    app = App.get_by_slug(slug)
    
    if app.submitter != g.user:
        flash(
            'You cannot edit an app that you are not the submitter of.',
            'error'
        )
        return redirect(url_for('app_manager.app_view', slug=app.slug), 303)

    if request.method == 'POST':
        app_description = request.form.get('app-desc', '').strip()

        try:
            AppDescriptionValidator.validate(app_description)
        except ValidationError as e:
            flash(str(e), 'error')
            return redirect(url_for('app_manager.app_edit', slug=app.slug), 303)

        app.edit(
            description=app_description
        )

        flash('App succesfully edited.', 'success')
        return redirect(url_for('app_manager.app_view', slug=slug), 303)
    
    return render_template('app_view/edit.html', app=app)


@app_manager.route('/apps/<slug>/change-visibility', methods=['GET', 'POST'])
@authenticated_required()
def change_visibility(slug):
    app = App.get_by_slug(slug)
    
    if app.submitter != g.user:
        flash(
            'You cannot edit an app that you are not the submitter of.',
            'error'
        )
        return redirect(url_for('app_manager.app_view', slug=app.slug), 303)

    if request.method == 'POST':
        visibility = request.form.get('visibility').strip()

        try:
            AppVisibilityValidator.validate(visibility)
        except ValidationError as e:
            flash(str(e), 'error')
            return redirect(url_for('app_manager.change_visibility', slug=app.slug), 303)

        # if app has no scripts, dont allow to make public
        if visibility != 'private' and len(app.scripts) == 0:
            flash('App must have at least one script to be made public', 'error')
            return redirect(url_for('app_manager.app_view', slug=app.slug), 303)

        app.visibility = visibility
        app.save()

        flash(f'App visibility successfully changed to {visibility}.', 'success')
        return redirect(url_for('app_manager.app_view', slug=app.slug), 303)

    return render_template(
        'app_view/change_visibility.html',
        app=app,
        visibility_options=supported_visibility_options,
    )

@app_manager.route('/apps/<slug>/scripts')
def app_scripts(slug):
    app = App.get_by_slug(slug)
    
    return render_template('app_view/scripts.html')

@app_manager.route('/apps/<slug>/add-script', methods=['get', 'post'])
@authenticated_required()
def add_script(slug):
    app = App.get_by_slug(slug)
    
    if app.submitter != g.user:
        flash(
            'You cannot add a script to an app that you are not the submitter of.',
            'error'
        )
        return redirect(url_for('app_manager.app_view', slug=app.slug), 303)

    if request.method == 'POST':

        script_action = request.form.get('script-action')
        # gets the comma seported list of distros sent by the user
        supported_distros = request.form.get('script-supported-distros', '')
        supported_distros = get_distros_from_string(supported_distros)
        script_content = request.form.get('script-content')

        try:
            ScriptActionValidator.validate(script_action)
            ScriptDistroValidator.validate_many(supported_distros)
            ScriptContentValidator.validate(script_content)
        except ValidationError as e:
            flash(str(e), 'error')
            return redirect(url_for('app_manager.add_script', slug=app.slug))
        
        Script.create(
            action=script_action,
            supported_distros=supported_distros,
            content=script_content,
            app=app
        )

        flash('Script successfully created.', 'success')
        return redirect(url_for('app_manager.app_view', slug=app.slug), 303)

    return render_template(
        'app_view/add_script.html',
        app=app,
        possible_script_actions=supported_script_actions
    )


@app_manager.route('/apps/<slug>/scripts/<int:script_id>/delete')
@authenticated_required()
def delete_script(slug, script_id):
    app = App.get_by_slug(slug)
    script = Script.get_by_id(script_id)
    
    if app.submitter != g.user:
        flash(
            'You cannot delete a script of an app that you are not the submitter of.',
            'error'
        )
        return redirect(url_for('app_manager.app_view', slug=app.slug), 303)

    if request.method == 'POST':
        script.delete_instance()
        flash('Script successfully deleted.', 'success')
        return redirect(url_for('app_mananger.app_view', slug=app.slug), 303)
    
    return render_template('app_view/delete_script.html', app=app, script=script)


@app_manager.route('/apps/<slug>/scripts/<int:script_id>/edit', methods=['GET', 'POST'])
@authenticated_required()
def edit_script(slug, script_id):
    app = App.get_by_slug(slug)
    script = Script.get_by_id(script_id)
    
    if app.submitter != g.user:
        flash(
            'You cannot edit a script of an app that you are not the submitter of.',
            'error'
        )
        return redirect(url_for('app_manager.app_view', slug=app.slug), 303)

    if request.method == 'POST':
        script_action = request.form.get('script-action')
        # gets the comma seported list of distros sent by the user
        supported_distros = request.form.get('script-supported-distros', '')
        supported_distros = get_distros_from_string(supported_distros)
        script_content = request.form.get('script-content')

        try:
            ScriptActionValidator.validate(script_action)
            ScriptDistroValidator.validate_many(supported_distros)
            ScriptContentValidator.validate(script_content)
        except ValidationError as e:
            flash(str(e), 'error')
            return redirect(url_for('app_manager.add_script', slug=app.slug), 303)

        script.edit(
            action=script_action,
            supported_distros=supported_distros,
            content=script_content,
        )

        flash('Script successfully edited.', 'success')
        return redirect(url_for('app_manager.app_view', slug=app.slug), 303)
    
    return render_template(
        'app_view/edit_script.html',
        app=app,
        script=script,
        possible_script_actions=supported_script_actions,
    )
