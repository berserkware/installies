from flask import Blueprint, abort, request
from installies.database.models import AppGroup
from installies.apps.app_manager.models import App, Script
from installies.apps.auth.models import User
from peewee import *

import json

api = Blueprint('api', __name__)

@api.route('/api/apps')
def apps():
    
    apps = AppGroup.get(**request.args)
    
    data = {
        "apps": []
    }

    for app in apps:
        app_data = app.serialize()
        app_data['works_on'] = app.works_on
        data['apps'].append(app_data)
        
    return data

@api.route('/api/app/<slug>')
def app(slug):
    
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
        
    data = app.serialize()
    data['scripts'] = []
    
    for script in app.scripts:
        script_data = script.serialize()
        
        data['scripts'].append(script_data)
        
    return data

@api.route('/api/user/<username>')
def user(username):
    
    try:
        user = (
            User
            .select()
            .where(User.username == username)
            .get()
        )
    except DoesNotExist:
        return abort(404)
        
    return user.serialize()
