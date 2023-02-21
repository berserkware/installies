from installies.apps.api.views import api
from installies.apps.app_library.views import app_library
from installies.apps.app_manager.views import app_manager
from installies.apps.auth.views import auth
from installies.globals import database
from installies.database.models import User
from flask import Flask, request, g, render_template
from peewee import *

app = Flask(__name__)

app.secret_key = '(j*&J6HtfJ$&hg&^__gEj'

@app.before_request
def before_request():
    database.connect()
    
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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)