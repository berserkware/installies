from flask import render_template, Blueprint, request, g, Response
from installies.lib.view import TemplateView
from installies.blueprints.app_manager.groups import AppGroup
from installies.blueprints.app_manager.models import App
from peewee import *

app_library = Blueprint('app_library', __name__)

class IndexView(TemplateView):
    template_path = 'index.html'

app_library.add_url_rule('/', 'index', view_func=IndexView.as_view())
    
@app_library.route('/apps')
def apps():
    apps = AppGroup.get(**request.args).where(App.visibility == 'public')
    
    return render_template('apps.html', apps=apps)
