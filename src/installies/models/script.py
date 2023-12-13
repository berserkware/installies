from peewee import (
    Model,
    CharField,
    TextField,
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
from installies.models.discussion import AppThread, Thread
from installies.config import database, apps_path
from installies.lib.url import make_slug
from installies.lib.random import gen_random_id
from installies.lib.shell import Shell
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

    creation_date = DateTimeField(default=datetime.now)
    last_modified = DateTimeField(default=datetime.now)
    submitter = ForeignKeyField(User, backref='scripts')
    maintainers = ForeignKeyField(Maintainers)
    description = CharField(255)

    filepath = CharField(255)
    shell = CharField(255)
    
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
    def create(
            cls,
            content: str,
            description: str,
            shell: str,
            submitter: User,
    ):
        """
        Create a Script object, and adds it to the database.

        :param content: The content of the script.
        :param description: The script's description.
        :param shell: The name of the shell the script is for.
        :param submitter: The submitter.
        """
        filepath = cls.create_script_file(apps_path, content)

        maintainers = Maintainers.create()
        
        created_script = super().create(
            maintainers=maintainers,
            submitter=submitter,
            filepath=filepath,
            description=description,
            shell=shell,
        )

        maintainers.add_maintainer(submitter)

        return created_script

    def edit(
            self,
            content: str,
            description: str,
            shell: str,
    ):
        """
        Edits the script.

        :param content: The new content.
        :param method: The script's method.
        :param shell: The name of the shell the script is for.
        """

        self.last_modified = datetime.today()

        self.description = description
        self.shell = shell
        self.save()

        with self.open_content('w') as f:
            f.write(content)

        self.save()

    def delete_instance(self):
        """Deletes the script and its related objects."""

        for script_report in self.reports:
            script_report.report.delete_instance()
        
        super().delete_instance()
        
        os.remove(self.filepath)
        
        self.votes.delete_instance()

    def serialize(self):
        """Turns the Script into a json serializable dict."""
        data = {}

        data['id'] = self.id
        data['shell'] = self.shell
        data['supported_distros'] = self.get_supported_distros_as_dict()
        data['creation_date'] = str(self.creation_date)
        data['last_modified'] = str(self.last_modified)
        
        with self.open_content() as c:
            data['content'] = c.read()
        
        data['submitter'] = self.submitter.username
        data['description'] = self.description

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

    def get_supported_distros_as_dict(self) -> dict:
        """
        Puts all the script's distros in a dictionary.

        The keys are the distro's architechture, and the values are lists of distro names.
        """

        distros = {}

        for distro in self.supported_distros:
            if distro.architecture_name not in distros.keys():
                distros[distro.architecture_name] = []

            distros[distro.architecture_name].append(distro.distro_name)
            
        return distros

    def get_supported_distros_as_string(self):
        """
        Turns the script's supported distros in the state the user would have entered them.

        Example: "distro:arch:arch, distro:arch:arch".
        """

        distros = {}
        for distro in self.supported_distros:
            if distro.distro_name not in distros.keys():
                distros[distro.distro_name] = []

            distros[distro.distro_name].append(distro.architecture_name)

        distro_strings = []
        for distro in distros:
            distro_strings.append(f'{distro}:{":".join(distros[distro])}')

        return ', '.join(distro_strings)

    
class AppScript(BaseModel):
    """A model for storing scripts for apps."""

    script = ForeignKeyField(Script, backref='app_data')
    app = ForeignKeyField(App, backref='scripts')
    version = CharField(64, null=True)
    use_default_function_matcher = BooleanField(default=True)
    thread = ForeignKeyField(Thread, backref='for_script')

    @classmethod
    def create(
            cls,
            script: Script,
            app,
            actions: list[str],
            version=None,
            use_default_function_matcher: bool=True,
    ):
        """
        Creates an AppScript.

        :param script: The script the AppScript object is for.
        :param app: The app the script is of.
        :param actions: The actions that the script supports.
        :param version: The version of the app the script is for.
        :param use_default_function_matcher: A boolean to mark if the
            script uses the function to action matcher.
        """
        thread = Thread.create(
            title=f'Discussion of script: "{script.description}"',
            creator=None,
        )
        app_thread = AppThread.create(
            thread=thread,
            app=app,
        )

        app_script = super().create(
            script=script,
            app=app,
            version=version,
            use_default_function_matcher=use_default_function_matcher,
            thread=thread,
        )

        actions = Action.create_from_list(app_script, actions)

        app.last_modified = datetime.today()
        app.save()

        return app_script


    def edit(
            self,
            actions: list[str],
            version=None,
            use_default_function_matcher: bool=True,
    ):
        """
        Edits an AppScript.

        :param actions: The actions that the script supports.
        :param version: The version of the app the script is for.
        :param use_default_function_matcher: A boolean to mark if the
            script uses the function to action matcher.
        """
        self.thread.title = f'Discussion of script: "{self.script.description}"'
        self.thread.save()
        
        self.version = version
        self.use_default_function_matcher = use_default_function_matcher

        Action.delete().where(Action.app_script == self).execute()
        Action.create_from_list(self, actions)

        self.app.last_modified = datetime.today()
        self.app.save()

        self.save()


    def delete_instance(self):
        deleted = super().delete_instance()

        self.script.delete_instance()
        self.thread.delete_instance()
        
        return deleted

    def add_function_matcher(self, content: str):
        """Adds the action to function matcher to the given content."""
        matcher = '\n'
        actions = self.actions

        shell = Shell.get_shell_by_name(self.script.shell)

        if shell.function_matcher_start is not '':
            matcher += f'{shell.function_matcher_start}\n\n'
        
        for action in actions:
            matcher += f'{shell.function_matcher_block}\n'.replace(
                '<action>', action.name
            )
        matcher += f'{shell.function_matcher_end}\n'

        matcher = matcher.replace(
            '<actions>',
            ' '.join([action.name for action in actions]),
        )
        
        return content + matcher
    
    def complete_content(self):
        """
        Adds the stuff to the script's content to make it working, returns the content.
        """
        with self.script.open_content() as f:
            new_content = f.read()

        shell = Shell.get_shell_by_name(self.script.shell)

        #adds the shebang
        shebang = f'#!{shell.interpreter_path} {shell.interpreter_arg}\n\n'
        new_content = shebang + new_content

        if self.use_default_function_matcher:
            new_content = self.add_function_matcher(new_content)

        return new_content

    def get_supported_actions(self):
        """Get the actions the script supports in a list."""
        return [action.name for action in self.actions]

    def serialize(self):
        """
        Gets the Scripts serialized data, including the extra data from the AppScript.

        :param version: The version for the complete_content method.
        """

        data = self.script.serialize()

        data['actions'] = [action.name for action in self.actions]
        data['for_version'] = self.version
        data['content'] = self.complete_content()

        return data


class Action(BaseModel):
    """A model for storing an action that an app script supports."""

    name = CharField(255)
    app_script = ForeignKeyField(AppScript, backref='actions', on_delete='CASCADE')

    @classmethod
    def create_from_list(cls, app_script: AppScript, actions: list[str]):
        """Creates multiple action objects from a list."""
        action_objects = []
        
        for action in actions:
            action_objects.append(Action.create(name=action, app_script=app_script))

        return action_objects
