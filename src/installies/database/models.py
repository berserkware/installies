from peewee import *
from installies.config import database, apps_path
from installies.lib.random import gen_random_id

import json
import bcrypt
import os

class BaseModel(Model):
    
    class Meta:
        database = database


class User(BaseModel):
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


class App(BaseModel):
    name = CharField(255, unique=True)
    slug = CharField(255, unique=True)
    description = TextField()
    creation_date = DateField()
    author = ForeignKeyField(User, backref='apps')

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
            for varient in script.varients:
                works_on.extend(varient.works_on_list)

        return works_on


class Script(BaseModel):
    action = CharField(255)
    works_on = CharField(255)
    filepath = CharField(255)
    public = BooleanField(default=False)
    app = ForeignKeyField(App, backref='scripts')

    def serialize(self, include_content=True):
        """Turn the Script into a json string."""
        data = {}

        data['action'] = self.action
        data['works_on'] = self.works_on_list

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
    def works_on_list(self):
        """Gets the distros the scripts works on in a list."""
        return json.loads(self.works_on)

    @classmethod
    def create_user_folder(cls, user: User):
        """
        Create a folder to store a user's apps if one does not exist already.

        The folder path is returned.

        :param user: The user to make the folder for.
        """
        user_dir = os.path.join(apps_path, user.username)
        if os.path.isdir(user_dir) is False:
            os.mkdir(user_dir)

        return user_dir

    @classmethod
    def create_app_folder(cls, app: App, apps_dir: str):
        """
        Create a folder to store an app's scripts if one does not exist already.

        The folder path is returned.

        :param app: The app to make the folder for.
        :param apps_dir: The directory to put the app folder in.
        """
        app_dir = os.path.join(apps_dir, app.slug)
        if os.path.isdir(app_dir) is False:
            os.mkdir(app_dir)

            return app_dir

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
                break

            with open(script_path, 'w') as f:
                f.write(script_content)

        return script_filename

    @classmethod
    def create(cls, **kwargs):
        """Create a Script object, and makes the files for the script."""
        app = kwargs['app']

        if 'content' in kwargs.keys():
            user_path = cls.create_user_folder(app.author)

            app_path = cls.create_app_folder(app, user_path)

            script_filepath = cls.create_script_file(
                app_path,
                kwargs['content']
            )

            kwargs['filepath'] = script_filepath

        return super().create(**kwargs)


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
