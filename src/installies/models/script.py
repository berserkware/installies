from peewee import (
    Model,
    CharField,
    DateTimeField,
    BooleanField,
    TextField,
    ForeignKeyField,
    JOIN,
)
from installies.models.base import BaseModel
from installies.models.user import User
from installies.models.app import App
from installies.config import database, apps_path
from installies.lib.url import make_slug
from installies.lib.random import gen_random_id
from datetime import datetime

import json
import os
import string
import random
import bleach

class ScriptNotFound(Exception):
    """An exception to raise when an app cannot be found."""

class Script(BaseModel):
    """A model for storing data about scripts."""

    action = CharField(255)
    last_modified = DateTimeField(default=datetime.now)
    filepath = CharField(255)
    version = CharField(64, null=True)
    app = ForeignKeyField(App, backref='scripts')
    
    @classmethod
    def get_by_id(cls, id: int):
        """
        Gets a script by its id.

        A ScriptNotFound error will be raised if it cannot be found.

        :param id: The id to get the script from.
        """

        script = (
            Script
            .select()
            .where(Script.id == id)
        )

        if script.exists() is False:
            raise ScriptNotFound

        return script.get()

    def open_content(self, mode='r'):
        """
        Get the content of the script.

        :param mode: The mode to opne the content in.
        """
        return open(self.filepath, mode)

    @classmethod
    def create_script_file(cls, app_dir: str, script_content: str):
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

                with open(script_path, 'w') as f:
                    f.write(script_content)

                break

        return script_path

    @classmethod
    def create(
            cls,
            action: str,
            supported_distros: list,
            content: str,
            app: App,
            version: str=None,
    ):
        """
        Create a Script object, and adds it to the database.

        :param action: The action that the script preforms.
        :param supported_distros: A list of distros that the script supports.
        :param content: The content of the script.
        :param version: The version of the app the script is for.
        :param app: The app the script is for.
        """
        app_dir = app.create_or_get_folder()

        script_path = cls.create_script_file(app_dir, content)

        created_script = super().create(
            action=action,
            filepath=script_path,
            version=version,
            app=app,
        )

        from installies.models.supported_distros import SupportedDistro
        SupportedDistro.create_from_list(supported_distros, created_script)

        app.last_modified = datetime.today()
        app.save()

        return created_script

    def edit(self, action: str, supported_distros: list, content: str, version: str=None):
        """
        Edits the script.

        :param action: The new action for the script.
        :param supported_distros: The new supported distros.
        :param content: The new content.
        """

        self.action = action
        self.last_modified = datetime.today()
        self.version = version

        # deletes and replaces the supported distros.
        from installies.models.supported_distros import SupportedDistro
        SupportedDistro.delete().where(SupportedDistro.script == self).execute()
        SupportedDistro.create_from_list(supported_distros, self)
        
        with self.open_content('w') as f:
            f.write(content)

        self.app.last_modified = datetime.today()
        self.app.save()

        self.save()

    def delete_instance(self):
        """Deletes the script and its related SupportedDistro objects."""

        from installies.models.supported_distros import SupportedDistro
        SupportedDistro.delete().where(SupportedDistro.script == self).execute()
        
        return super().delete_instance()

    def get_all_supported_distros(self) -> dict:
        """
        Gets all the script's supported distros, and puts them in a dictionary.

        The keys are the distro's architechture, and the values are lists of distro names.
        """

        distros = {}

        for distro in self.supported_distros:
            if distro.architechture_name not in distros.keys():
                distros[distro.architechture_name] = []

            distros[distro.architechture_name].append(distro.distro_name)
            
        return distros


    def get_supported_distro_string(self):
        """
        Gets the supported distro in the state the user entered it.

        Example: "distro:arch:arch, distro:arch:arch".
        """

        distros = {}
        for distro in self.supported_distros:
            if distro.distro_name not in distros.keys():
                distros[distro.distro_name] = []

            distros[distro.distro_name].append(distro.architechture_name)

        distro_strings = []
        for distro in distros:
            distro_strings.append(f'{distro}:{":".join(distros[distro])}')

        return ', '.join(distro_strings)


    def serialize(self):
        """Turns the Script into a json serializable dict."""
        data = {}

        data['action'] = self.action
        data['supported_distros'] = self.get_all_supported_distros()
        data['last_modified'] = str(self.last_modified)
        data['for_version'] = self.version
        with self.open_content() as c:
            data['content'] = c.read()

        return data
