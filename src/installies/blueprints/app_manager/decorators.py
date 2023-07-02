from installies.models.app import App
from installies.models.script import Script
from functools import wraps
from flask import abort
from peewee import JOIN

def get_app_from_arg(arg_name: str='slug'):
    """
    A decorator for views that gets an app from an arg passed into the view function.

    It will replace the arg with the app. It searchs in the slug field of the app. If
    the app cannot be found, a 404 error is raised.

    :param arg_name: The name of the arg to get the app from.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            app_slug = kwargs[arg_name]

            app = (
                App
                .select()
                .join(Script, JOIN.LEFT_OUTER)
                .where(App.slug == app_slug)
            )

            if app.exists() is False:
                abort(404)

            app = app.get()

            kwargs['app'] = app
            del kwargs[arg_name]

            return func(*args, **kwargs)

        return wrapper
    return decorator


def get_script_from_arg(arg_name: str='script_id'):
    """
    A decorator for views that gets a script from an arg passed into the view function.

    It will replace the arg with the script. It searches in the id field of the script. If
    the script cannot be found, a 404 error is raised.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            script_id = kwargs[arg_name]

            script = Script.select().where(Script.id == script_id)

            if script.exists() is False:
                abort(404)

            script = script.get()

            kwargs['script'] = script
            del kwargs[arg_name]

            return func(*args, **kwargs)

        return wrapper
    return decorator
