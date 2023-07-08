from flask import Blueprint, abort, request, g
from installies.groups.app import AppGroup
from installies.groups.script import ScriptGroup
from installies.groups.modifiers import Paginate
from installies.models.app import App, AppNotFound
from installies.models.script import Script
from peewee import *

import json
import re

api = Blueprint('api', __name__)

@api.route('/api/apps')
def apps():
    apps = AppGroup().get(**request.args).where(App.visibility == 'public')

    data = {
        'apps': []
    }

    paginator = Paginate(
         default_per_page = 10,
         max_per_page = 50,
     )

    apps = paginator.modify(apps, **request.args)

    for app in apps:
        data['apps'].append(app.serialize())

    return data

@api.route('/api/apps/<app_name>/scripts')
def scripts(app_name):
    app = App.select().where(App.name == app_name)

    if app.exists() is False:
        abort(404)

    app = app.get()

    if app.visibility == 'private' and app.submitter != g.user:
        abort(404)

    scripts = ScriptGroup.get(**request.args).where(Script.app == app)

    data = {
        'scripts': []
    }

    if 'version' in request.args.keys() and re.match(app.version_regex, request.args['version']) is None:
        data['error'] = "VersionDoesNotMatchRegex"
        return data
        
    for script in scripts:
        serialized_script = script.serialize()
        
        if 'version' in request.args.keys():
            serialized_script['content'] = serialized_script['content'].replace('<version>', request.args['version'])
        else:
            serialized_script['content'] = serialized_script['content'].replace('<version>', script.app.current_version)

        data['scripts'].append(serialized_script)

    return data
