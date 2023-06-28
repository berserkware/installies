from flask import Blueprint, abort, request, g
from installies.blueprints.app_manager.groups import AppGroup, ScriptGroup
from installies.blueprints.app_manager.models import App, Script, AppNotFound
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

    for app in apps:
        data['apps'].append(app.serialize())

    return data

@api.route('/api/apps/<slug>/scripts')
def scripts(slug):
    app = App.select().where(App.slug == slug)

    if app.exists() is False:
        abort(404)

    app = app.get()

    if app.visibility == 'private' and app.submitter != g.user:
        abort(404)

    scripts = ScriptGroup.get(**request.args).where(Script.app == app)

    data = {
        'scripts': []
    }

    for script in scripts:
        serialized_script = script.serialize()
        
        if 'version' in request.args.keys():
            if re.fullmatch(script.app.version_regex, request.args['version']) is None:
                data['error'] = "VersionDoesNotMatchRegex"
                continue

            serialized_script['content'] = serialized_script['content'].replace('<version>', request.args['version'])
        else:
            serialized_script['content'] = serialized_script['content'].replace('<version>', script.app.current_version)

        data['scripts'].append(serialized_script)

    return data
