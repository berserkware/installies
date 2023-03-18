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
from installies.apps.app_manager.validate import (
    AppNameValidator,
    AppDescriptionValidator,
    ScriptActionValidator,
    ScriptDistroValidator,
    ScriptContentValidator
)
from installies.config import supported_script_actions
from installies.database.models import App, Script
from peewee import JOIN

app_manager = Blueprint('app_manager', __name__)

@app_manager.route('/create-app', methods=['GET', 'POST'])
def create_app():
    # Makes sure user is authenticated
    if g.is_authed is False:
        return redirect('/login')

    if request.method == 'POST':
        app_name = request.form.get('app-name', '').strip()
        app_description = request.form.get('app-desc', '').strip()

        # returns error to user if app name is not clean
        try:
            AppNameValidator.validate(app_name)
            AppDescriptionValidator.validate(app_description)
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('app_manager.createapp'))

        # cleans the app name and description,
        # to make sure there is no malicious stuff
        app_name = bleach.clean(app_name)
        app_description = bleach.clean(app_description)

        app = App.create(app_name, app_description, g.user)

        return redirect(url_for('app_manager.app_view', slug=app.slug))

    return render_template('create_app.html')


@app_manager.route('/apps/<slug>', methods=['GET', 'POST'])
def app_view(slug):
    app = (
        App
        .select()
        .join(Script, JOIN.LEFT_OUTER)
        .where(App.slug == slug)
    )

    if app.exists() is False:
        abort(404)

    app = app.get()

    return render_template('app_view/info.html', app=app)


@app_manager.route('/apps/<slug>/delete', methods=['GET', 'POST'])
def app_delete(slug):

    if g.is_authed is False:
        return redirect('/login')
    
    app = (
        App
        .select()
        .join(Script, JOIN.LEFT_OUTER)
        .where(App.slug == slug)
    )

    if app.exists() is False:
        abort(404)
    
    app = app.get()

    if app.author != g.user:
        flash(
            'You cannot delete an app you have not authored.',
            'error'
        )
        return redirect(url_for('app_manager.app_view', slug=app.slug))

    if request.method == 'POST':
        app.delete_instance()
        flash('App successfully deleted!', 'success')
        return redirect('/')

    return render_template('app_view/delete.html', app=app)


@app_manager.route('/apps/<slug>/edit', methods=['GET', 'POST'])
def app_edit(slug):

    if g.is_authed is False:
        return redirect('/login')
    
    app = (
        App
        .select()
        .join(Script, JOIN.LEFT_OUTER)
        .where(App.slug == slug)
    )

    if app.exists() is False:
        abort(404)
    
    app = app.get()

    if app.author != g.user:
        flash(
            'You cannot edit an app you have not authored.',
            'error'
        )
        return redirect(url_for('app_manager.app_view', slug=app.slug))

    if request.method == 'POST':
        app_description = request.form.get('app-desc', '').strip()

        try:
            AppDescriptionValidator.validate(app_description)
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('app_manager.app_edit', slug=app.slug))

        app_description = bleach.clean(app_description)

        app.edit(
            description=app_description
        )

        flash('App succesfully edited.', 'success')
        return redirect(url_for('app_manager.app_view', slug=slug))
    
    return render_template('app_view/edit.html', app=app)


@app_manager.route('/apps/<slug>/make-public', methods=['GET', 'POST'])
def make_app_public(slug):

    if g.is_authed is False:
        return redirect('/login')
    
    app = (
        App
        .select()
        .join(Script, JOIN.LEFT_OUTER)
        .where(App.slug == slug)
    )

    if app.exists() is False:
        abort(404)
    
    app = app.get()

    if app.author != g.user:
        flash(
            'You cannot change the visibility of an app your are not the author of.',
            'error'
        )
        return redirect(url_for('app_manager.app_view', slug=app.slug))

    if request.method == 'POST':
        if len(app.scripts) == 0:
            flash(
                'App must have at least one script to make it public.',
                'error'
            )
            return redirect(url_for('app_manager.app_view', slug=app.slug))

        app.public = True
        app.save()

        flash(
            'App successfully made public.',
            'success'
        )
        return redirect(url_for('app_manager.app_view', slug=app.slug))

    return render_template('app_view/make_public.html', app=app)


@app_manager.route('/apps/<slug>/make-private', methods=['GET', 'POST'])
def make_app_private(slug):

    if g.is_authed is False:
        return redirect('/login')
    
    app = (
        App
        .select()
        .join(Script, JOIN.LEFT_OUTER)
        .where(App.slug == slug)
    )

    if app.exists() is False:
        abort(404)
    
    app = app.get()

    if app.author != g.user:
        flash(
            'You cannot change the visibility of an app your are not the author of.',
            'error'
        )
        return redirect(url_for('app_manager.app_view', slug=app.slug))

    if request.method == 'POST':
        app.public = False
        app.save()

        flash(
            'App successfully made private.',
            'success'
        )
        return redirect(url_for('app_manager.app_view', slug=app.slug))

    return render_template('app_view/make_private.html', app=app)

@app_manager.route('/apps/<slug>/scripts')
def app_scripts(slug):
    return render_template('app_view/scripts.html')

@app_manager.route('/apps/<slug>/add-script', methods=['get', 'post'])
def add_script(slug):

    if g.is_authed is False:
        return redirect('/login')

    app = (
        App
        .select()
        .join(Script, JOIN.LEFT_OUTER)
        .where(App.slug == slug)
    )

    if app.exists() is False:
        abort(404)

    app = app.get()

    if app.author != g.user:
        flash(
            'You cannot add a script to an app you have not authored.',
            'error'
        )
        return redirect(f'/apps/{slug}/')

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
        except ValueError as e:
            flash(str(e), 'error')
            return redirect('app_manager.add_script', slug=app.slug)

        Script.create(
            action=script_action,
            supported_distros=supported_distros,
            content=script_content,
            app=app
        )

        flash('Script successfully created.', 'success')
        return redirect(url_for('app_manager.app_view', slug=app.slug))

    return render_template(
        'app_view/add_script.html',
        app=app,
        possible_script_actions=supported_script_actions
    )


@app_manager.route('/apps/<slug>/scripts/<int:script_id>/delete')
def delete_script(slug, script_id):

    if g.is_authed is False:
        return redirect('/login')
    
    app = App.get(App.slug == slug)
    script = Script.select().where(Script.id == script_id).get()

    if app.author != g.user:
        flash(
            'You cannot delete a script of an app you have not authored.',
            'error'
        )
        return redirect(url_for('app_manager.app_view', slug=app.slug))

    if request.method == 'POST':
        script.delete_instance()
        flash('Script successfully deleted.', 'success')
        return redirect(url_for('app_mananger.app_view', slug=app.slug))
    
    return render_template('app_view/delete_script.html', app=app, script=script)


@app_manager.route('/apps/<slug>/scripts/<int:script_id>/edit', methods=['GET', 'POST'])
def edit_script(slug, script_id):

    if g.is_authed is False:
        return redirect('/login')
    
    app = App.get(App.slug == slug)
    script = Script.select().where(Script.id == script_id).get()

    if app.author != g.user:
        flash(
            'You cannot edit a script of an app you have not authored.',
            'error'
        )
        return redirect(url_for('app_manager.app_view', slug=app.slug))

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
        except ValueError as e:
            flash(str(e), 'error')
            return redirect('app_manager.add_script', slug=app.slug)

        script.edit(
            action=script_action,
            supported_distros=supported_distros,
            content=script_content,
        )

        flash('Script successfully edited.', 'success')
        return redirect(url_for('app_manager.app_view', slug=app.slug))
    
    return render_template(
        'app_view/edit_script.html',
        app=app,
        script=script,
        possible_script_actions=supported_script_actions,
    )


