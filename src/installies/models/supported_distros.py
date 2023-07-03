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
from installies.models.script import Script
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
    
