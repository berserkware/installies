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
from installies.models.maintainer import Maintainers
from installies.models.discussion import Thread
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
    method = CharField(255, unique=True)
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
    def create(cls, directory: str, content: str, method: str, distros: dict, actions: list[str]):
        """Creates the script data."""

        filepath = cls.create_script_file(directory, content)

        supported_distros = SupportedDistrosJunction.create()
        supported_distros.create_from_list(distros)
        
        script_data =  super().create(
            filepath=filepath,
            method=method,
            supported_distros=supported_distros,
        )

        actions = Action.create_from_list(script_data, actions)

        return script_data

    def delete_instance(self):
        Action.delete().where(Action.script_data == self).execute()
        os.remove(self.filepath)
        super().delete_instance()
        self.supported_distros.delete_instance()

    def get_supported_actions(self):
        """Get the actions the script supports in a list."""
        return [action.name for action in self.actions]


class Action(BaseModel):
    """A model for storing an action that a script supports."""

    name = CharField(255)
    script_data = ForeignKeyField(ScriptData, backref='actions')

    @classmethod
    def create_from_list(cls, script_data: ScriptData, actions: list[str]):
        """Creates multiple action objects from a list."""
        action_objects = []
        
        for action in actions:
            action_objects.append(Action.create(name=action, script_data=script_data))

        return action_objects
    
    
class Script(BaseModel):
    """A model for storing data about scripts."""

    creation_date = DateTimeField(default=datetime.now)
    last_modified = DateTimeField(default=datetime.now)
    version = CharField(64, null=True)
    script_data = ForeignKeyField(ScriptData)
    thread = ForeignKeyField(Thread)
    submitter = ForeignKeyField(User, backref='scripts')
    maintainers = ForeignKeyField(Maintainers)
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
            supported_distros: list,
            content: str,
            method: str,
            actions: list[str],
            submitter: User,
            app: App,
            version: str=None,
    ):
        """
        Create a Script object, and adds it to the database.

        :param supported_distros: A list of distros that the script supports.
        :param content: The content of the script.
        :param method: The method the script uses.
        :param actions: The actions that the script supports.
        :param submitter: The submitter.
        :param app: The app the script is for.
        :param version: The version of the app the script is for.
        """
        app_dir = app.create_or_get_folder()
        
        script_data = ScriptData.create(app_dir, content, method, supported_distros, actions)

        maintainers = Maintainers.create()

        thread = Thread.create(
            title=f'Discussion of script with method "{method}"',
            app=app,
            creator=None,
        )
        
        created_script = super().create(
            version=version,
            script_data=script_data,
            thread=thread,
            maintainers=maintainers,
            submitter=submitter,
            app=app,
        )

        maintainers.add_maintainer(submitter)

        app.last_modified = datetime.today()
        app.save()

        return created_script

    def edit(
            self,
            supported_distros: list,
            content: str,
            method: str,
            actions: str,
            version: str=None
    ):
        """
        Edits the script.

        :param supported_distros: The new supported distros.
        :param content: The new content.
        :param method: The script's method.
        :param actions: The sctions that the script supports.
        :param version: The version of the app the script is for.
        """

        self.last_modified = datetime.today()
        self.version = version

        self.script_data.supported_distros.delete_all_distros()
        self.script_data.supported_distros.create_from_list(supported_distros)

        self.thread.title = f'Discussion of script with method "{method}"'
        self.thread.save()

        Action.delete().where(Action.script_data == self.script_data).execute()
        Action.create_from_list(self.script_data, actions)
        
        with self.script_data.open_content('w') as f:
            f.write(content)

        self.script_data.method = method

        self.app.last_modified = datetime.today()
        self.app.save()

        self.save()

    def delete_instance(self):
        """Deletes the script and its related SupportedDistro objects."""
        
        super().delete_instance()

        self.script_data.delete_instance()

    def serialize(self):
        """Turns the Script into a json serializable dict."""
        data = {}

        data['id'] = self.id
        data['actions'] = [action.name for action in self.script_data.actions]
        data['supported_distros'] = self.script_data.supported_distros.get_as_dict()
        data['last_modified'] = str(self.last_modified)
        data['for_version'] = self.version
        with self.script_data.open_content() as c:
            data['content'] = c.read()
        data['submitter'] = self.submitter.username
        data['method'] = self.script_data.method

        return data

    def can_user_edit(self, user: User):
        """
        Check if the given user is allowed to edit the script.
        """
        if user is None:
            return False

        if user.admin is True:
            return True

        if self.maintainers.is_maintainer(user):
            return True

        return False


    def complete_content(self, version=None):
        """
        Adds the stuff to the script's content to make it working, returns the content.

        It replaces <version> with the given version. If the version is None, it uses the
        app's current_version. Adds the action function matcher to the end of the content.

        :param version: The version of the script to install.
        """
        with self.script_data.open_content() as f:
            new_content = f.read()

        #replaces the version
        if version is not None:
            new_content = new_content.replace('<version>', version)
        elif self.app.current_version is not None:
            new_content = new_content.replace('<version>', self.app.current_version)

        action_switcher = """\n"""
        # adds the action function matcher
        for action in self.script_data.actions:
            action_name = action.name
            if_statement = f"""
if [ \"$1\" == \"{action_name}\" ]; then
    {action_name}
fi\n"""
            action_switcher += if_statement

        new_content += action_switcher

        return new_content

            
        
