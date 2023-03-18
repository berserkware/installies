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


class User(BaseModel):
    """A model for storing data about users."""

    username = CharField(255, unique=True)
    email = CharField(255, unique=True)
    password = CharField(255)
    creation_date = DateField()
    token = CharField(255, unique=True)
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
    def make_token(cls):
        """Create a 50 letter long string of random letters and numbers."""
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for i in range(50))

    @classmethod
    def create(cls, username: str, email: str, password: str, admin: bool=False):
        """
        Create a User, and saves it to the database.

        :param username: The user's username.
        :param email: The user's email.
        :param password: The user's password.
        :param admin: The user's admin status.
        """
        creation_date = date.today()

        token = cls.make_token()

        hashed_pass = cls.hash_password(password)

        return super().create(
            username=username,
            email=email,
            password=hashed_pass,
            creation_date=creation_date,
            token=token,
            admin=admin
        )


class App(BaseModel):
    """A class for storing app data."""

    name = CharField(255, unique=True)
    slug = CharField(255, unique=True)
    description = TextField()
    creation_date = DateField()
    last_modified = DateField()
    author = ForeignKeyField(User, backref='apps')
    public = BooleanField(default=False)

    @classmethod
    def create(self, name: str, description: str, author: User):
        """
        Create a App object, and adds it to the database.

        :param name: The name of the app.
        :param description: The app's description.
        :param author: The app's author.
        """
        slug = make_slug(name)

        creation_date = date.today()

        return super().create(
            name=name,
            slug=slug,
            description=description,
            creation_date=creation_date,
            last_modified=creation_date,
            author=author
        )

    def serialize(self):
        """Turn the App into a json string."""
        data = {}

        data['name'] = self.name
        data['slug'] = self.slug
        data['description'] = self.description
        data['creation_date'] = self.creation_date
        data['author_username'] = self.author.username

        return data

    @property
    def works_on(self):
        """All the distros that the app works on in a list."""
        works_on = []

        for script in self.scripts:
            works_on.extend(script.works_on_list)

        return works_on

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

        self.description = description

        self.last_modified = date.today()

        self.save()

    def delete_instance(self):
        """Delete the app and all of its scripts."""

        for script in self.scripts:
            script.delete_instance()

        super().delete_instance()


class Script(BaseModel):
    """A model for storing data about scripts."""

    action = CharField(255)
    supported_distros = CharField(255)
    filepath = CharField(255)
    app = ForeignKeyField(App, backref='scripts')

    def serialize(self, include_content=True):
        """Turn the Script into a json string."""
        data = {}

        data['action'] = self.action
        data['supported_distros'] = self.supported_distros_list

        if include_content:
            with self.open_content() as f:
                data['content'] = f.read()

        return data

    def open_content(self, mode='r'):
        """
        Get the content of the script.

        :param mode: The mode to opne the content in.
        """
        return open(self.filepath, mode)

    @property
    def supported_distros_list(self):
        """Gets the distros the script supports in a list."""
        return json.loads(self.supported_distros)

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

        # serializes the distros with json
        supported_distros = json.dumps(supported_distros)

        created_script = super().create(
            action=action,
            supported_distros=supported_distros,
            filepath=script_path,
            app=app
        )

        self.app.last_modified = date.today()
        self.app.save()

        return created_scrupt

    def edit(self, action: str, supported_distros: list, content: str):
        """
        Edits the script.

        :param action: The new action for the script.
        :param supported_distros: The new supported distros.
        :param content: The new content.
        """

        self.action = action
        self.supported_distros = json.dumps(supported_distros)
        with self.open_content('w') as f:
            f.write(content)

        self.app.last_modified = date.today()
        self.app.save()

        self.save()


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
        """
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
