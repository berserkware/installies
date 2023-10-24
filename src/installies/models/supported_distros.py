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
from installies.config import database, apps_path
from installies.lib.url import make_slug
from installies.lib.random import gen_random_id
from datetime import datetime

import json
import os
import string
import random
import bleach


class SupportedDistro(BaseModel):
    """A model for storing a supported distro of a script."""

    script = ForeignKeyField(Script, backref="supported_distros", on_delete="CASCADE")
    distro_name = CharField(255)
    architecture_name = CharField(255)

    @classmethod
    def create_from_dict(cls, script: Script, distros: dict):
        """
        Creates multiple supported distros from a dictionary.

        :param script: The script the distros are for.
        :param distros: A dictionary of the distros and their architectures.
        """

        supported_distros = []

        for distro in distros.keys():
            architectures = distros[distro]
            if architectures == []:
                architectures = ['*']

            for architecture in architectures:
                supported_distro = SupportedDistro.create(
                    script=script,
                    distro_name=distro,
                    architecture_name=architecture,
                )
                supported_distros.append(supported_distro)

        return supported_distros

    @classmethod
    def get_dict_from_string(cls, distro_string: str) -> dict:
        """
        Gets a dictonary of supported distros and their architectures.

        The distro string should be formatted as "distro1:arch1:arch2, distro2:arch1:arch2". It
        will return a dictionary where the keys are the distros, and the values are a list of
        architectures.

        :param distro_string: A comma separated list of distros.
        """
        strings = distro_string.split(',')

        distros = {}
        for string in strings:
            split_string = string.split(':')
            distro_name = split_string[0].strip()

            # adds to `distros` dict continues loop if there are no architectures
            if len(split_string) <= 1:
                distros[distro_name] = []
                continue

            architectures = []
            for i, value in enumerate(split_string):
                # skips the first element
                if i == 0:
                    continue;

                architectures.append(value)

            distros[distro_name] = architectures
            
        return distros
