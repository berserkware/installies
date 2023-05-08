from installies.apps.app_manager.models import App, Script
from installies.database.group import Group
from installies.database.modifiers import SortBy, ByColumn, SearchInAttributes, InAttribute
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
