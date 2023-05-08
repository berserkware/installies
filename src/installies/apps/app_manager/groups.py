from installies.apps.app_manager.models import App, Script, SupportedDistro, Distro
from installies.database.group import Group
from installies.database.modifiers import SortBy, ByColumn, SearchInAttributes
from datetime import datetime

class AppGroup(Group):
    """
    A class for getting multiple App objects from the database.
    """

    modifiers = [
        SortBy(
            model=App,
            allowed_attributes = [
                'slug',
                'description',
                'creation_date',
                'last_modified',
                'submitter',
            ],
            default_attribute = 'slug',
            default_order = 'asc',
        ),
        ByColumn(
            model = App,
            kwarg_name = 'slug',
            attribute = 'slug',
        ),
        ByColumn(
            model = App,
            kwarg_name = 'creation_date',
            attribute = 'creation_date',
            converter = datetime.fromisoformat,
        ),
        ByColumn(
            model = App,
            kwarg_name = 'last_modified',
            attribute = 'last_modified',
            converter = datetime.fromisoformat,
        ),
        SearchInAttributes(
            model = App,
            allowed_attributes = [
                'slug',
                'description'
            ],
            default_attribute = 'slug',
        ),
    ]
    model = App

    @classmethod
    def get(cls, **kwargs):
        """
        A modified version of the default get method.

        It add supported for getting apps by their supported distros.
        """

        query = super().get(**kwargs)

        # gets the supported distros of the app to get
        supports = kwargs.get('supports')

        #gets the supported Distro object
        distro = Distro.select().where(Distro.slug == supports)

        if distro.exists() is False:
            return query

        distro = distro.get()

        query = query.join(SupportedDistro).join(Distro)

        return query.filter(Distro.id == distro.id)


class ScriptGroup(Group):
    """
    A class for getting multiple Script objects from the database.
    """

    modifiers = [
        SortBy(
            model = Script,
            allowed_attributes = [
                'action'
            ],
            default_attribute = 'action',
            default_order = 'asc',
        ),
        ByColumn(
            model = Script,
            kwarg_name = 'action',
            attribute = 'action',
        ),
    ]
    model = Script
