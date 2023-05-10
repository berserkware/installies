from flask import render_template, Blueprint, request, g, Response
from installies.apps.app_manager.groups import AppGroup
from installies.apps.app_manager.models import App
from peewee import *

app_library = Blueprint('app_library', __name__)

@app_library.route('/')
def index():
    return render_template('index.html')
    
@app_library.route('/apps')
def apps():
    apps = AppGroup.get(**request.args).where(App.visibility == 'public')
    
    return render_template('apps.html', apps=apps)
