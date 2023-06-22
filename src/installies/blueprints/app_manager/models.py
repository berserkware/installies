from peewee import (
    Model,
    CharField,
    DateTimeField,
    BooleanField,
    TextField,
    ForeignKeyField,
    JOIN,
)
from installies.database.models import BaseModel
from installies.blueprints.auth.models import User
from installies.config import database, apps_path
from installies.lib.url import make_slug
from installies.lib.random import gen_random_id
from datetime import datetime

import json
import os
import string
import random
import bleach

class AppNotFound(Exception):
    """An exception to raise when an app cannot be found."""

class ScriptNotFound(Exception):
    """An exception to raise when an app cannot be found."""
    
class App(BaseModel):
    """A class for storing app data."""

    name = CharField(255, unique=True)
    slug = CharField(255, unique=True)
    description = TextField()
    creation_date = DateTimeField(default=datetime.now)
    last_modified = DateTimeField(default=datetime.now)
    submitter = ForeignKeyField(User, backref='apps')
    visibility = CharField(255, default='private')

    @classmethod
    def get_by_slug(cls, slug: str):
        """
        Gets an app by its slug.

        An AppNotFound error is raised if it cannot be found.

        :param slug: The slug to get the app by.
        """

        app = (
            App
            .select()
            .join(Script, JOIN.LEFT_OUTER)
            .where(App.slug == slug)
        )

        if app.exists() is False:
            raise AppNotFound

        return app.get()
    
    @classmethod
    def create(cls, name: str, description: str, submitter: User):
        """
        Create a App object, and adds it to the database.

        The data is also cleaned.

        :param name: The name of the app.
        :param description: The app's description.
        :param submitter: The app's submitter.
        """
        name = bleach.clean(name)
        description = bleach.clean(description)
        
        slug = make_slug(name)

        app = super().create(
            name=name,
            slug=slug,
            description=description,
            submitter=submitter,
        )

        # adds the user as a maintainer
        Maintainer.create(app=app, user=submitter)
        
        return app

    def serialize(self):
        """Turn the App into a json serializable dict."""
        data = {}

        data['name'] = self.name
        data['slug'] = self.slug
        data['description'] = self.description
        data['creation_date'] = str(self.creation_date)
        data['last_modified'] = str(self.last_modified)
        data['submitter'] = self.submitter.username

        return data

    def create_or_get_folder(self, apps_dir: str=apps_path):
        """
        Create a folder for the app if it does not exist.

        Returns the path to the app folder.

        :param apps_dir: The directory to put the apps in.
        """
        app_path = os.path.join(apps_dir, self.slug)
        if os.path.isdir(app_path) is False:
            os.mkdir(app_path)

        return app_path

    def edit(self, description: str):
        """
        Edits the app.

        :param description: The new description for the app.
        """

        description = bleach.clean(description)
        
        self.description = description

        self.last_modified = datetime.today()

        self.save()

    def delete_instance(self):
        """Delete the app and all of its scripts."""

        for script in self.scripts:
            script.delete_instance()

        for maintainer in self.maintainers:
            maintainer.delete_instance()

        super().delete_instance()

    def can_user_edit(self, user: User):
        """
        Check if the given user is allowed to edit the app.
        """
        if user is None:
            return False

        if user.admin is True:
            return True

        maintainer = (
            Maintainer.select()
            .where(Maintainer.user == user)
            .where(Maintainer.app == self)
        )

        if maintainer.exists() is True:
            return True

        return False


class Script(BaseModel):
    """A model for storing data about scripts."""

    action = CharField(255)
    last_modified = DateTimeField(default=datetime.now)
    filepath = CharField(255)
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
            app: App
    ):
        """
        Create a Script object, and adds it to the database.

        :param action: The action that the script preforms.
        :param supported_distros: A list of distros that the script supports.
        :param content: The content of the script.
        :param app: The app the script is for.
        """
        app_dir = app.create_or_get_folder()

        script_path = cls.create_script_file(app_dir, content)

        created_script = super().create(
            action=action,
            filepath=script_path,
            app=app
        )

        SupportedDistro.create_from_list(supported_distros, created_script)

        app.last_modified = datetime.today()
        app.save()

        return created_script

    def edit(self, action: str, supported_distros: list, content: str):
        """
        Edits the script.

        :param action: The new action for the script.
        :param supported_distros: The new supported distros.
        :param content: The new content.
        """

        self.action = action
        self.last_modified = datetime.today()

        # deletes and replaces the supported distros.
        SupportedDistro.delete().where(SupportedDistro.script == self).execute()
        SupportedDistro.create_from_list(supported_distros, self)
        
        with self.open_content('w') as f:
            f.write(content)

        self.app.last_modified = datetime.today()
        self.app.save()

        self.save()

    def delete_instance(self):
        """Deletes the script and its related SupportedDistro objects."""

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
        data['supported_distros'] = self.get_all_supported_distro_names()
        data['last_modified'] = str(self.last_modified)
        with self.open_content() as c:
            data['content'] = c.read()

        return data


class Distro(BaseModel):
    """A model for storing data about a linux distribution."""

    name = CharField(255)
    slug = CharField(255)
    based_on = ForeignKeyField('self', null=True, backref='derivitives')

    @staticmethod
    def get_all_distro_slugs() -> list:
        """
        Gets a list of slugs of all the possible distros.
        """

        slugs = []
        
        for distro in Distro.select():
            slugs.append(distro.slug)
        
        return slugs

class SupportedDistro(BaseModel):
    """A model for storing a supported distro of a script."""

    script = ForeignKeyField(Script, backref='supported_distros')
    app = ForeignKeyField(App, backref='supported_distros')
    distro_name = CharField(255)
    architechture_name = CharField(255)

    @classmethod
    def create_from_list(cls, distros: dict, script: Script):
        """
        Creates mutliple supported distros from a list of distro slugs.

        A list of the created SupportedDistro objects are returned.
        
        :param distros: A dictionary of the distros and their architechtures.
        :param script: The Script to make the SupportedDistro objects for.
        """

        supported_distros = []

        for distro in distros.keys():
            architechtures = distros[distro]
            if architechtures == []:
                architechtures = ['*']

            for architechture in architechtures:
                alternate_name = (AlternativeArchitechtureName
                                  .select()
                                  .where(AlternativeArchitechtureName.name == architechture)
                                  )
                
                if alternate_name.exists():
                    # gets the main name of the architechutre
                    architechture = alternate_name.get().architechture.name

                supported_distro = SupportedDistro.create(
                    script=script,
                    app=script.app,
                    distro_name=distro,
                    architechture_name=architechture,
                )
                supported_distros.append(supported_distro)

        return supported_distros


class Architechture(BaseModel):
    """A model for storing infomation about a cpu architechture."""

    name = CharField(255)
    
    @classmethod
    def get_all_architechture_names(cls):
        """Gets a list of all the architechture names."""
        names = []
        for architechture in cls.select():
            names.append(architechture.name)

        return names


class AlternativeArchitechtureName(BaseModel):
    """A model for storing alternative names for architechtures."""

    name = CharField(255)
    architechture = ForeignKeyField(Architechture, backref='alternative_names')
    

class Maintainer(BaseModel):
    """A model for storing maintainer infomation."""

    user = ForeignKeyField(User, backref='maintains')
    app = ForeignKeyField(App, backref='maintainers')
