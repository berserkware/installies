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
from installies.models.voting import VoteJunction
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


class Shell(BaseModel):
    """A model for storing a shell that a script supports."""

    name = CharField(255)
    file_extension = CharField(255)
    file_mimetype = CharField(255)
    interpreter_path = CharField(255)
    interpreter_arg = CharField(255)

    #action to function matcher fields

    # this is code that runs no matter the action. It can
    # be used to import the modules to get the cli args.
    function_matcher_start = TextField()
    # The code is added for each action the script supports. when this
    # is added <action> get replaced with the action the block is for.
    # It should call the function to run the action.
    function_matcher_block = TextField()
    # This is code to run if the user didn't select a supported function.
    function_matcher_end = TextField()

    @classmethod
    def get_all_names(cls) -> list[str]:
        """Gets the names of all the shells in a list."""
        return [shell.name for shell in Shell.select()] 

    
class Script(BaseModel):
    """A model for storing data about scripts."""

    creation_date = DateTimeField(default=datetime.now)
    last_modified = DateTimeField(default=datetime.now)
    submitter = ForeignKeyField(User, backref='scripts')
    maintainers = ForeignKeyField(Maintainers)
    description = CharField(255)
    votes = ForeignKeyField(VoteJunction)

    filepath = CharField(255)
    shell = ForeignKeyField(Shell, backref="scripts")
    use_default_function_matcher = BooleanField(default=True)
    
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
            actions: list[str],
            shell: Shell,
            submitter: User,
            use_default_function_matcher: bool=True,
    ):
        """
        Create a Script object, and adds it to the database.

        :param content: The content of the script.
        :param description: The script's description.
        :param actions: The actions that the script supports.
        :param shell: The shell the script is for.
        :param submitter: The submitter.
        """
        filepath = cls.create_script_file(apps_path, content)

        votes = VoteJunction.create()

        maintainers = Maintainers.create()
        
        created_script = super().create(
            maintainers=maintainers,
            submitter=submitter,
            filepath=filepath,
            description=description,
            votes=votes,
            shell=shell,
            use_default_function_matcher=use_default_function_matcher,
        )

        actions = Action.create_from_list(created_script, actions)
        maintainers.add_maintainer(submitter)

        return created_script

    def edit(
            self,
            content: str,
            description: str,
            actions: list[str],
            shell: Shell,
            use_default_function_matcher: bool=True,
    ):
        """
        Edits the script.

        :param content: The new content.
        :param method: The script's method.
        :param actions: The sctions that the script supports.
        :param shell: The shell the script is for.
        :param use_default_function_matcher: True if you want to use the default function matcher.
        """

        self.last_modified = datetime.today()
        self.use_default_function_matcher = use_default_function_matcher

        self.description = description
        self.shell = shell
        self.save()

        Action.delete().where(Action.script == self).execute()
        Action.create_from_list(self, actions)

        with self.open_content('w') as f:
            f.write(content)

        self.save()

    def delete_instance(self):
        """Deletes the script and its related objects."""
        
        Action.delete().where(Action.script == self).execute()
        
        super().delete_instance()
        
        os.remove(self.filepath)
        
        self.votes.delete_instance()

    def serialize(self):
        """Turns the Script into a json serializable dict."""
        data = {}

        data['id'] = self.id
        data['actions'] = [action.name for action in self.actions]
        data['shell'] = self.shell.name
        data['supported_distros'] = self.get_supported_distros_as_dict()
        data['creation_date'] = str(self.creation_date)
        data['last_modified'] = str(self.last_modified)
        
        if self.app_data.exists():
            data['for_version'] = self.app_data.get().version
        
        with self.open_content() as c:
            data['content'] = c.read()
        data['submitter'] = self.submitter.username
        data['description'] = self.description
        data['score'] = self.votes.score

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


    def add_function_matcher(self, content: str):
        """Adds the action to function matcher to the given content."""
        matcher = ''

        matcher += f'{self.shell.function_matcher_start}\n\n'
        for action in self.actions:
            matcher += f'{self.shell.function_matcher_block}\n'.replace(
                '<action>', action.name
            )
        matcher += f'\n{self.shell.function_matcher_end}\n'

        matcher = matcher.replace(
            '<actions>',
            ' '.join([action.name for action in self.actions]),
        )
        
        return content + matcher
    

    def complete_content(self, version=None):
        """
        Adds the stuff to the script's content to make it working, returns the content.

        It replaces <version> with the given version. If the version is None, it uses the
        app's current_version. It also adds a shebang.

        :param version: The version of the script to install.
        """
        with self.open_content() as f:
            new_content = f.read()

        #replaces the version
        if version is not None:
            new_content = new_content.replace('<version>', version)
        elif self.app_data.get().app.current_version is not None:
            new_content = new_content.replace(
                '<version>',
                self.app_data.get().app.current_version
            )

        #adds the shebang
        shebang = f'#!{self.shell.interpreter_path} {self.shell.interpreter_arg}\n\n'
        new_content = shebang + new_content

        if self.use_default_function_matcher:
            new_content = self.add_function_matcher(new_content)

        return new_content


    def get_supported_actions(self):
        """Get the actions the script supports in a list."""
        return [action.name for action in self.actions]

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


class Action(BaseModel):
    """A model for storing an action that a script supports."""

    name = CharField(255)
    script = ForeignKeyField(Script, backref='actions')

    @classmethod
    def create_from_list(cls, script: Script, actions: list[str]):
        """Creates multiple action objects from a list."""
        action_objects = []
        
        for action in actions:
            action_objects.append(Action.create(name=action, script=script))

        return action_objects

    
class AppScript(BaseModel):
    """A model for storing scripts for apps."""

    script = ForeignKeyField(Script, backref='app_data')
    app = ForeignKeyField(App, backref='scripts')
    version = CharField(64, null=True)
    thread = ForeignKeyField(Thread, backref='for_script')

    @classmethod
    def create(cls, script: Script, app, version=None):
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
            thread=thread,
        )

        app.last_modified = datetime.today()
        app.save()

        return app_script


    def edit(self, version=None, **kwargs):
        self.thread.title = f'Discussion of script: "{self.script.description}"'
        self.thread.save()
        
        self.version = version 

        self.app.last_modified = datetime.today()
        self.app.save()

        self.save()


    def delete_instance(self, **kwargs):
        deleted = super().delete_instance()

        self.script.delete_instance()
        self.thread.delete_instance()
        
        return deleted
