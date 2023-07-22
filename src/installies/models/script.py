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
from installies.models.supported_distros import SupportedDistrosJunction
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


class ScriptData(BaseModel):
    """A model for storing the path to the script content."""

    filepath = CharField(255)
    supported_distros = ForeignKeyField(SupportedDistrosJunction)

    def open_content(self, mode='r'):
        """
        Get the content of the script.

        :param mode: The mode to open the content in.
        """
        return open(self.filepath, mode)

    @classmethod
    def create_script_file(cls, directory: str, content: str):
        """
        Create a file to store the data for the script.

        The path is returned.

        :param directory: The directory to put the script in.
        :param content: The content of the script.
        """
        script_filename = ''
        script_path = ''

        # since script file names are randomly generated there is a slight
        # chance that it generates the name of a script file that already
        # exists.
        while True:
            script_filename = f'script-{gen_random_id()}'

            script_path = os.path.join(directory, script_filename)

            if os.path.exists(script_path) is False:

                with open(script_path, 'w') as f:
                    f.write(content)

                break

        return script_path


    @classmethod
    def create(cls, directory: str, content: str, distros: dict):
        """Creates the script data."""

        filepath = cls.create_script_file(directory, content)

        supported_distros = SupportedDistrosJunction.create()
        supported_distros.create_from_list(distros)
        
        return super().create(
            filepath=filepath,
            supported_distros=supported_distros,
        )
    
    
class Script(BaseModel):
    """A model for storing data about scripts."""

    action = CharField(255)
    last_modified = DateTimeField(default=datetime.now)
    version = CharField(64, null=True)
    script_data = ForeignKeyField(ScriptData)
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
        
        script_data = ScriptData.create(app_dir, content, supported_distros)
        
        created_script = super().create(
            action=action,
            version=version,
            script_data=script_data,
            app=app,
        )

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

        self.script_data.supported_distros.delete_all_distros()
        self.script_data.supported_distros.create_from_list(supported_distros)
        
        with self.script_data.open_content('w') as f:
            f.write(content)

        self.app.last_modified = datetime.today()
        self.app.save()

        self.save()

    def delete_instance(self):
        """Deletes the script and its related SupportedDistro objects."""
        
        super().delete_instance()

        self.script_data.delete_instance()

        self.script_data.supported_distros.delete_instance()


    def serialize(self):
        """Turns the Script into a json serializable dict."""
        data = {}

        data['action'] = self.action
        data['supported_distros'] = self.script_data.supported_distros.get_as_dict()
        data['last_modified'] = str(self.last_modified)
        data['for_version'] = self.version
        with self.script_data.open_content() as c:
            data['content'] = c.read()

        return data
