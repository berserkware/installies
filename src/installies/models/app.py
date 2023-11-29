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
from installies.models.maintainer import Maintainers
from installies.config import database, apps_path
from installies.lib.url import make_slug
from installies.lib.random import gen_random_id
from datetime import datetime

import json
import os
import string
import random
import bleach


class App(BaseModel):
    """A class for storing app data."""

    name = CharField(255, unique=True)
    display_name = CharField(255, null=True)
    description = TextField()
    creation_date = DateTimeField(default=datetime.now)
    last_modified = DateTimeField(default=datetime.now)
    submitter = ForeignKeyField(User, backref='apps')
    maintainers = ForeignKeyField(Maintainers)
    
    @classmethod
    def create(
            cls,
            name: str,
            description: str,
            submitter: User,
            display_name: str=None,
    ):
        """
        Create a App object, and adds it to the database.

        The data is also cleaned.

        :param name: The name of the app.
        :param display_name: The display_name of the App
        :param description: The app's description.
        :param submitter: The app's submitter.
        """
        name = bleach.clean(name)
        description = bleach.clean(description)

        maintainers = Maintainers.create()
        
        app = super().create(
            name=name,
            display_name=display_name,
            description=description,
            submitter=submitter,
            maintainers=maintainers,
        )

        maintainers.add_maintainer(submitter)
        
        return app

    def serialize(self):
        """Turn the App into a json serializable dict."""
        data = {}

        data['id'] = self.id
        data['name'] = self.name
        data['display_name'] = self.display_name
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
        app_path = os.path.join(apps_dir, self.name)
        if os.path.isdir(app_path) is False:
            os.mkdir(app_path)

        return app_path

    def edit(self, description: str, display_name: str):
        """
        Edits the app.

        :param description: The new description for the app.
        :param display_name: The new display name.
        """

        description = bleach.clean(description)
        
        self.description = description
        self.display_name = display_name

        self.last_modified = datetime.today()

        self.save()

    def delete_instance(self):
        """Delete the app and all of its scripts."""

        for script in self.scripts:
            script.delete_instance()

        for thread in self.threads:
            thread.delete_instance()
        
        super().delete_instance()

        self.maintainers.delete_instance()

    def can_user_edit(self, user: User):
        """
        Check if the given user is allowed to edit the app.
        """
        if user is None:
            return False

        if user.admin is True:
            return True

        if self.maintainers.is_maintainer(user):
            return True

        return False
