import bleach

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
    create_app,
    )
from installies.apps.app_manager.validate import (
    AppNameValidator,
    AppDescriptionValidator,
)
from installies.database.models import App, Script
from peewee import JOIN, DoesNotExist

app_manager = Blueprint('app_manager', __name__)


@app_manager.route('/createapp', methods=['GET', 'POST'])
def createapp():
    # Makes sure user is authenticated
    if g.is_authed is False:
        return redirect('/login')

    if request.method == 'POST':
        app_name = request.form.get('app-name', '').strip()

        # returns error to user if app name is not clean
        try:
            AppNameValidator.validate(app_name)
        except ValueError as e:
            flash(str(e), 'error')
            return render_template(
                'create_app.html',
            )

        app_description = request.form.get('app-desc', '').strip()

        # returns error to user if app desctiption is not clean
        try:
            AppDescriptionValidator.validate(app_description)
        except ValueError as e:
            flash(str(e), 'error')
            return render_template(
                'create_app.html',
            )

        # cleans the app name and description,
        # to make sure there is no malicious stuff

        app_name = bleach.clean(app_name)
        app_description = bleach.clean(app_description)

        # creates the app to be put in the database
        app = create_app(app_name, app_description, g.user.id)

        # adds the app to the database, and gets its id
        app.save()

        return redirect(url_for('app_view', app.slug))

    return render_template('create_app.html')


@app_manager.route('/apps/<slug>')
def app_view(slug):
    try:
        app = (
            App
            .select()
            .join(Script, JOIN.LEFT_OUTER)
            .where(App.slug == slug)
            .get()
            )
    except DoesNotExist:
        return abort(404)

    return render_template('app_view.html', app=app)


@app_manager.route('/apps/<slug>/delete')
def app_delete(slug):
    return render_template('delete_app.html')


@app_manager.route('/apps/<slug>/edit', methods=['GET', 'POST'])
def app_edit(slug):
    return render_template('edit_app.html')


@app_manager.route('/apps/<slug>/makepublic')
def make_app_public(slug):
    pass

@app_manager.route('/apps/<slug>/makeprivate')
def make_app_private(slug):
    pass


@app_manager.route('/apps/<slug>/addscript')
def add_script(slug):
    return render_template('add_script.html')


@app_manager.route('/apps/<slug>/script/<int:script_id>/delete')
def delete_script(slug, script_id):
    return render_template('delete_script.html')


@app_manager.route('/apps/<slug>/script/<int:script_id>/edit')
def edit_script(slug, script_id):
    return render_template('edit_script.html')
