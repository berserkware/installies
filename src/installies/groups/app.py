from installies.models.app import App
from installies.models.maintainer import Maintainer, Maintainers
from installies.models.script import Script
from installies.models.supported_distros import SupportedDistro
from installies.models.user import User
from installies.groups.base import Group
from installies.groups.modifiers import (
    SearchableField,
    SearchInFields,
    BySupportedDistro,
    Paginate,
)
from datetime import datetime

class AppGroup(Group):
    """
    A class for getting multiple Script objects from the database.
    """

    model = App

    @classmethod
    def get(cls, params, query=None):
        # gets the base query
        if query is None:
            query = cls.model.select()

        # gets the app by a certain field
        if params.get('name', '') is not '':
            query = query.where(
                (cls.model.name == params.get('name'))
            )

        if params.get('display_name', '') is not '':
            query = query.where(
                (cls.model.display_name == params.get('display_name'))
            )

        if params.get('last_modified', '') is not '':
            query = query.where(
                (cls.model.last_modified == datetime.fromisoformat(params.get('last_modified')))
            )

        if params.get('creation_date', '') is not '':
            query = query.where(
                (cls.model.creation_date == datetime.fromisoformat(params.get('creation_date')))
            )


        # sorts the query
        sort_by = params.get('sort-by', 'name')
        order_by = params.get('order-by', 'asc')

        # the field to sort the object by
        sort_by_field = None

        # gets the field to sort by
        match sort_by:
            case 'name':
                sort_by_field = cls.model.name
            case 'description':
                sort_by_field = cls.model.description
            case 'creation_date':
                sort_by_field = cls.model.creation_date
            case 'last_modified':
                sort_by_field = cls.model.last_modified
            case 'submiter':
                sort_by_field = cls.model.submitter
            case _:
                sort_by_field = cls.model.name

        # orders and sorts the query
        if order_by == 'desc':
            query = query.order_by(sort_by_field.desc())
        else:
            query = query.order_by(sort_by_field)

        # gets the apps by search
        search_modifier = SearchInFields(
            model = App,
            searchable_fields = [
                SearchableField('name'),
                SearchableField('description'),
                SearchableField(
                    'maintainers',
                    lambda model, name, data: Maintainer.user.username.contains(data),
                    models=[Maintainers, Maintainer, User],
                ),
                SearchableField(
                    'submitter',
                    lambda model, name, data: getattr(model, name).username.contains(data),
                    models=[User],
                ),
            ],
            default_field = 'name',
        )

        query = search_modifier.modify(query, params)
        query = query.switch(cls.model)


        return query.distinct()
