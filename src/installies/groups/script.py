from installies.models.app import App
from installies.models.script import Script
from installies.models.supported_distros import SupportedDistro, Distro
from installies.models.user import User
from installies.groups.base import Group
from installies.groups.modifiers import (
    JoinModifier,
    SortBy,
    ByColumn,
    SearchableAttribute,
    SearchInAttributes,
    BySupportedDistro,
    Paginate,
    BySupportedAction,
)
from datetime import datetime

class ScriptGroup(Group):
    """
    A class for getting multiple Script objects from the database.
    """

    modifiers = [
        SortBy(
            model = Script,
            allowed_attributes = [
                'version',
                'last_modified',
            ],
            default_attribute = 'last_modified',
            default_order = 'asc',
        ),
        ByColumn(
            model = Script,
            kwarg_name = 'version',
            attribute = 'version'
        ),
        ByColumn(
            model = Script,
            kwarg_name = 'last_modified',
            attribute = 'last_modified',
            converter = datetime.fromisoformat,
        ),
        BySupportedDistro(),
        BySupportedAction(),
    ]
    model = Script
