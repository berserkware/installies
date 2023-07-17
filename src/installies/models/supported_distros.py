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
from installies.models.script import ScriptData
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

    script_data = ForeignKeyField(ScriptData, backref='supported_distros')
    app = ForeignKeyField(App, backref='supported_distros')
    distro_name = CharField(255)
    architecture_name = CharField(255)

    @classmethod
    def create_from_list(cls, distros: dict, script_data: ScriptData, app: App):
        """
        Creates mutliple supported distros from a list of distro slugs.

        A list of the created SupportedDistro objects are returned.
        
        :param distros: A dictionary of the distros and their architectures.
        :param script_data: The ScriptData object.
        :param app: The app for the supported_distro.
        """

        supported_distros = []

        for distro in distros.keys():
            architectures = distros[distro]
            if architectures == []:
                architectures = ['*']

            for architecture in architectures:
                alternate_name = (AlternativeArchitectureName
                                  .select()
                                  .where(AlternativeArchitectureName.name == architecture)
                                  )
                
                if alternate_name.exists():
                    # gets the main name of the architechutre
                    architecture = alternate_name.get().architecture.name

                supported_distro = SupportedDistro.create(
                    script_data=script_data,
                    app=app,
                    distro_name=distro,
                    architecture_name=architecture,
                )
                supported_distros.append(supported_distro)

        return supported_distros


class Architecture(BaseModel):
    """A model for storing infomation about a cpu architecture."""

    name = CharField(255)
    
    @classmethod
    def get_all_architecture_names(cls):
        """Gets a list of all the architechture names."""
        names = []
        for architecture in cls.select():
            names.append(architecture.name)

        return names


class AlternativeArchitectureName(BaseModel):
    """A model for storing alternative names for architectures."""

    name = CharField(255)
    architecture = ForeignKeyField(Architecture, backref='alternative_names')
    
