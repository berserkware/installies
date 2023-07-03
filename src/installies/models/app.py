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

class App(BaseModel):
    """A class for storing app data."""

    name = CharField(255, unique=True)
    slug = CharField(255, unique=True)
    description = TextField()
    current_version = CharField(255, null=True)
    version_regex = CharField(255, null=True)
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
    def create(
            cls,
            name: str,
            description: str,
            submitter: User,
            current_version: str=None,
            version_regex: str=None,
    ):
        """
        Create a App object, and adds it to the database.

        The data is also cleaned.

        :param name: The name of the app.
        :param description: The app's description.
        :param submitter: The app's submitter.
        :param current_version: The app's current version.
        :param version_regex: The regex to check user-submitted app versions.
        """
        name = bleach.clean(name)
        description = bleach.clean(description)
        
        slug = make_slug(name)

        app = super().create(
            name=name,
            slug=slug,
            description=description,
            submitter=submitter,
            current_version=current_version,
            version_regex=version_regex,
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
        data['current_version'] = self.current_version
        data['version_regex'] = self.version_regex
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

    def edit(self, description: str, current_version: str, version_regex: str):
        """
        Edits the app.

        :param description: The new description for the app.
        :param current_version: The new current version.
        :param version_regex: The new version regex for the the app.
        """

        description = bleach.clean(description)
        
        self.description = description
        self.current_version = current_version
        self.version_regex = version_regex

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


class Maintainer(BaseModel):
    """A model for storing maintainer infomation."""

    user = ForeignKeyField(User, backref='maintains')
    app = ForeignKeyField(App, backref='maintainers')
