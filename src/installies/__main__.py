from installies.apps.api.views import api
from installies.apps.app_library.views import app_library
from installies.apps.app_manager.blueprint import app_manager
from installies.apps.auth.views import auth
from installies.apps.admin.views import admin
from installies.config import database
from installies.apps.auth.models import User
from installies.config import (
    supported_script_actions,
    supported_visibility_options,
)
from flask import Flask, request, g, render_template
from peewee import *

app = Flask(__name__)

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.secret_key = '(j*&J6HtfJ$&hg&^__gEj'

@app.before_request
def before_request():
    database.connect()

    g.supported_script_actions = supported_script_actions
    g.supported_visibility_options = supported_visibility_options
    
    token = request.cookies.get('user-token')

    # Checks that cookie exists
    if token is None:
        g.is_authed = False
        g.user = None
    
    try:
        user = User.get(User.token == token)
        g.is_authed = True
        g.user = user
    except DoesNotExist:
        g.is_authed = False
        g.user = None


@app.after_request
def after_request(response):
    database.close()
    return response
    
@app.errorhandler(404)
def pagenotfound(e):
    return render_template('404.html'), 404

app.register_blueprint(api)
app.register_blueprint(app_library)
app.register_blueprint(app_manager)
app.register_blueprint(auth)
app.register_blueprint(admin)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
