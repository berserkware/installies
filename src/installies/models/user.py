from peewee import (
    Model,
    CharField,
    DateField,
    BooleanField,
    DateTimeField,
    ForeignKeyField,
)
from installies.models.base import BaseModel
from installies.config import database, apps_path
from installies.lib.random import gen_random_id
from installies.lib.url import make_slug
from datetime import datetime

import json
import bcrypt
import os
import string
import random

class User(BaseModel):
    """A model for storing data about users."""

    username = CharField(255, unique=True)
    email = CharField(255, unique=True)
    password = CharField(255)
    creation_date = DateTimeField(default=datetime.now)
    verified = BooleanField(default=False)
    admin = BooleanField(default=False)

    def match_password(self, password: str) -> bool:
        """
        Return True if the password matches the User's password, else not.

        :param password: The password to check if matches.
        """
        bytes_pass = password.encode('utf8')

        bytes_user_pass = self.password.encode('utf8')

        return bcrypt.checkpw(bytes_pass, bytes_user_pass)

    def serialize(self):
        """Put the data of the object into a dictionary."""
        data = {}

        data['username'] = self.username
        data['creation_date'] = self.creation_date
        data['admin'] = self.admin

        return data

    @classmethod
    def hash_password(cls, password: str):
        """
        Hashes a password, and returns the hashed password in a string.

        :param password: The password to hash.
        """
        byte_pass = password.encode('utf8')
        salt = bcrypt.gensalt()

        password = bcrypt.hashpw(byte_pass, salt)
        return password.decode('utf-8')

    @classmethod
    def create(cls, username: str, email: str, password: str, admin: bool=False):
        """
        Create a User, and saves it to the database.

        :param username: The user's username.
        :param email: The user's email.
        :param password: The user's password.
        :param admin: The user's admin status.
        """

        hashed_pass = cls.hash_password(password)

        return super().create(
            username=username,
            email=email,
            password=hashed_pass,
            admin=admin
        )


class Session(BaseModel):
    """A model for storing session data."""

    user = ForeignKeyField(User, backref="sessions")
    token = CharField(255, unique=True)

    @classmethod
    def create(cls, user):
        while True:
            token = cls.make_token()

            if Session.select().where(Session.token == token).exists():
                continue

            break

        return super().create(
            user=user,
            token=token
        )

    @classmethod
    def make_token(cls):
        """Create a 50 letter long string of random letters and numbers."""
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for i in range(50))
