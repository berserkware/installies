from flask import Blueprint, abort, request, g
from installies.groups.app import AppGroup
from installies.groups.script import ScriptGroup
from installies.groups.modifiers import Paginate
from installies.models.app import App
from installies.models.script import Script, AppScript
from peewee import *

import json
import re

api = Blueprint('api', __name__)

@api.route('/api/apps')
def apps():
    apps = AppGroup().get(params=request.args)

    data = {
        'apps': []
    }

    paginator = Paginate(
         default_per_page = 10,
         max_per_page = 50,
     )

    apps = paginator.modify(apps, params=request.args)

    for app in apps:
        data['apps'].append(app.serialize())

    return data

@api.route('/api/apps/<app_name>/scripts')
def scripts(app_name):
    app = App.select().where(App.name == app_name)

    if app.exists() is False:
        abort(404)

    app = app.get()

    scripts = ScriptGroup.get(
        params=request.args,
        query=Script.select().join(AppScript).where(AppScript.app == app)
    )

    paginator = Paginate(
        default_per_page = 10,
        max_per_page = 50,
    )

    scripts = paginator.modify(scripts, params=request.args)

    data = {
        'scripts': []
    }

    for script in scripts:
        serialized_script = script.serialize()
        serialized_script['content'] = script.complete_content(request.args.get('version'))
        data['scripts'].append(serialized_script)

    return data
