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


class SupportedDistrosJunction(BaseModel):
    """A junction models between SupportedDistro models and scripts."""


    def get_as_dict(self) -> dict:
        """
        Gets all the distros, and put's them in a dictionary.

        The keys are the distro's architechture, and the values are lists of distro names.
        """

        distros = {}

        for distro in self.distros:
            if distro.architecture_name not in distros.keys():
                distros[distro.architecture_name] = []

            distros[distro.architecture_name].append(distro.distro_name)
            
        return distros

    def get_as_string(self):
        """
        Gets the distros in the state the user entered it.

        Example: "distro:arch:arch, distro:arch:arch".
        """

        distros = {}
        for distro in self.distros:
            if distro.distro_name not in distros.keys():
                distros[distro.distro_name] = []

            distros[distro.distro_name].append(distro.architecture_name)

        distro_strings = []
        for distro in distros:
            distro_strings.append(f'{distro}:{":".join(distros[distro])}')

        return ', '.join(distro_strings)
    
    def create_from_list(self, distros: dict):
        """
        Creates mutliple supported distros from a list of distro slugs.
        
        :param distros: A dictionary of the distros and their architectures.
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
                    group=self,
                    distro_name=distro,
                    architecture_name=architecture,
                )
                supported_distros.append(supported_distro)

        return supported_distros

    def delete_all_distros(self):
        """Delete all the distros related to this."""

        SupportedDistro.delete().where(SupportedDistro.group == self).execute()

    def delete_instance(self):
        self.delete_all_distros()
        super().delete_instance()
    

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

    group = ForeignKeyField(SupportedDistrosJunction, backref="distros")
    distro_name = CharField(255)
    architecture_name = CharField(255)
    

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
    
