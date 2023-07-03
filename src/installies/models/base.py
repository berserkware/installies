from peewee import (
    Model,
    CharField,
    DateField,
    BooleanField,
    TextField,
    ForeignKeyField,
)
from installies.config import database, apps_path
from installies.lib.random import gen_random_id
from installies.lib.url import make_slug
from datetime import date

import json
import bcrypt
import os
import string
import random


class BaseModel(Model):
    """A base class that defines the default database for the models to use."""

    class Meta:
        """Meta data for the BaseModel."""

        database = database
