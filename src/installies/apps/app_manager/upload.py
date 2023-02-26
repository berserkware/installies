from installies.config import (
    supported_distros,
    database,
    apps_path
)
from installies.database.models import User, App, Script
from installies.lib.url import make_slug
from installies.lib.random import gen_random_id
from datetime import date
from peewee import *

import os
import json


def get_distros_from_string(distros: str):
    """
    Get a list of distros from a comma separated list.

    :param distros: A comma separated list of distros.
    """
    # puts the supported distros into a list
    script_supported_distros = distros.split(',')

    # strips the distros of spaces
    striped_distros = []
    for distro in script_supported_distros:
        if distro != '':
            striped_distros.append(distro.strip())

    return striped_distros


def create_user_folder(user: User):
    """
    Create a folder to store a user's apps if one does not exist already.

    The folder path is returned.

    :param user: The user to make the folder for.
    """
    user_dir = os.path.join(apps_path, user.username)
    if os.path.isdir(user_dir) is False:
        os.mkdir(user_dir)

    return user_dir


def create_app_folder(app: App, apps_dir: str):
    """
    Create a folder to store an app's scripts if one does not exist already.

    The folder path is returned.

    :param app: The app to make the folder for.
    :param apps_dir: The directory to put the app folder in.
    """
    app_dir = os.path.join(apps_dir, app.slug)
    if os.path.isdir(app_dir) is False:
        os.mkdir(app_dir)

    return app_dir


def create_script_file(app_dir: str, script_content: str):
    """
    Create a file to store the data for the script.

    The path is returned.

    :param app_dir: The directory of the app the script is for.
    :param script_content: The content of the script.
    """
    script_filename = ''
    script_path = ''

    # since script file names are randomly generated there is a slight
    # chance that it generates the name of a script file that already
    # exists.
    while True:
        script_filename = f'script-{gen_random_id()}'

        script_path = os.path.join(app_dir, script_filename)

        if os.path.exists(script_path) is False:
            break

    with open(script_path, 'w') as f:
        f.write(script_content)

    return script_filename

def create_app(name: str, description: str, author_id: int) -> App:
    """
    Creates an App object.
    
    :param name: The name of the app.
    :param description: The app description.
    :param author_id: The id of the author of the script.
    """
    
    # creates a slug out of the name of the script
    slug = make_slug(name)
    
    # gets the creation date of the app
    creation_date = date.today()
    
    author = User.get(User.id == author_id)
    
    app = App(
        name=name,
        slug=slug,
        description=description,
        creation_date=creation_date,
        author=author
    )
    
    create_app_folder(app)
    
    return app
