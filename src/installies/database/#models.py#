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


class AppGroup:
    """A class for retrieving multiple apps from the database."""

    @classmethod
    def get_page(cls, apps, size: int, page: int):
        """
        Get a page of apps.

        :param app: The apps to get the page from.
        :param size: The amount of apps per page.
        :param page: The page number.
        """
        return apps.paginate(page, size)

    @classmethod
    def sort_by_creation_date(cls, apps, order_by: str='desc'):
        """a
        Sort the apps by their creation_date.

        :param apps: The apps to sort.
        :param order_by: asc or desc, which way to order. Defualt is
            desc.
        """
        if order_by == 'asc':
            return apps.order_by(App.creation_date.asc())
        else:
            return apps.order_by(App.creation_date.desc())

    @classmethod
    def sort_by_slug(cls, apps, order_by: str='desc'):
        """
        Sorts the apps by their name slug.

        :param apps: The apps to sort.
        :param order_by: asc or desc, which way to order. Defualt is
            desc.
        """
        if order_by == 'asc':
            return apps.order_by(App.slug.asc())
        else:
            return apps.order_by(App.creation_date.desc())

    @classmethod
    def sort(cls, apps, sort_by: str='creation_date', order_by: str='desc'):
        """
        Sorts the apps.

        You can sort the apps specific way using the sort_by param.
        Options:

        - creation_date - Sorts the apps by their creation_date.

        :param apps: The apps to sort.
        :param sort_by: What to sort by.
        :param order_by: What to order by. asc or desc. Default is
            desc.
        """
        if sort_by == 'creation_date':
            return cls.sort_by_creation_date(apps, order_by)
        elif sort_by == 'slug':
            return cls.sort_by_slug(apps, order_by)

        return apps

    @classmethod
    def get(cls, **kwargs):
        """
        Get a list of apps. You can filter and sort apps using kwargs.

        Possible filters:

        - size: The amount of apps per page. This is maxed out 
            to 100.
        - page: The page number.
        - sort_by: What to sort the apps by. Default is creation_date.
        - order_by: What to order the apps by. desc or asc. Default is
            asc.
        - author: Gets only the apps by the user with the username.
        """
        apps = App.select().join(User)
        sort_by = kwargs.get('sort_by', 'creation_date')
        order_by = kwargs.get('order_by', 'desc')
        apps = cls.sort(apps, sort_by, order_by)

        size = kwargs.get('size', '20')
        try:
            size = int(size)
        except ValueError:
            size = 20
        page = kwargs.get('page', '1')
        try:
            page = int(page)
        except ValueError:
            page = 1
        apps = cls.get_page(apps, size, page)

        author = kwargs.get('author')
        if author is not None:
            apps = apps.where(App.author.username == author)

        return apps.distinct()
