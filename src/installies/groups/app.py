from installies.models.app import App, Maintainer
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
)
from datetime import datetime

class AppGroup(Group):
    """
    A class for getting multiple App objects from the database.
    """

    modifiers = [
        JoinModifier(models=[User, Maintainer]),
        SortBy(
            model = App,
            allowed_attributes = [
                'name',
                'description',
                'creation_date',
                'last_modified',
                'submitter',
            ],
            default_attribute = 'name',
            default_order = 'asc',
        ),
        ByColumn(
            model = App,
            kwarg_name = 'name',
            attribute = 'name',
        ),
        ByColumn(
            model = App,
            kwarg_name = 'display_name',
            attribute = 'display_name',
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
            searchable_attributes = [
                SearchableAttribute('name'),
                SearchableAttribute('description'),
                SearchableAttribute(
                    'maintainers',
                    lambda model, name, data: Maintainer.user.username.contains(data),
                ),
                SearchableAttribute(
                    'submitter',
                    lambda model, name, data: getattr(model, name).username.contains(data),
                ),
            ],
            default_attribute = 'name',
        ),
        BySupportedDistro(),
        Paginate(
            default_per_page = 10,
            max_per_page = 50,
        )
    ]
    model = App
