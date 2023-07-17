from installies.models.app import App, Maintainer
from installies.models.script import AppScript
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
)
from datetime import datetime

class AppScriptGroup(Group):
    """
    A class for getting multiple AppScript objects from the database.
    """

    modifiers = [
        SortBy(
            model = AppScript,
            allowed_attributes = [
                'action',
                'version',
                'last_modified',
            ],
            default_attribute = 'last_modified',
            default_order = 'asc',
        ),
        ByColumn(
            model = AppScript,
            kwarg_name = 'action',
            attribute = 'action',
        ),
        ByColumn(
            model = AppScript,
            kwarg_name = 'version',
            attribute = 'version'
        ),
        ByColumn(
            model = AppScript,
            kwarg_name = 'last_modified',
            attribute = 'last_modified',
            converter = datetime.fromisoformat,
        ),
        BySupportedDistro(),
    ]
    model = AppScript
