from peewee import Query
from installies.models.app import App
from installies.models.script import Script, ScriptData, Action, Shell
from installies.models.supported_distros import SupportedDistro, SupportedDistrosJunction
from functools import reduce

import typing as t

class Modifier:
    """
    A base class for modifying Query objects with user submitted params.

    This class defines the standard for all modifier classes to follow.
    """

    def modify(self, query: Query, params):
        """
        A method for modifying SelectQuerys.

        It should take a query, modify it with the params, and return it.
        """

        return query


class JoinModifier(Modifier):
    """
    A modifier to join models to the query.

    :param models: The models to join.
    """

    def __init__(self, models: list):
        self.models = models

    def modify(self, query: Query, params):
        for model in self.models:
            query = query.join(model)

        return query

    
class SortBy(Modifier):
    """
    A modifier class for sorting and ordering the SelectQuery by either ascending or descending.

    :param model: The model to sort by.
    :param allowed_attributes: The attributes that the objects can be sorted by.
    :param default_attribute: The attribute that the objects are softed by by default.
    :param default_order: The order that the objects are ordered by by default.
    """

    def __init__(self, model, allowed_attributes, default_attribute, default_order='asc'):
        self.model = model
        self.allowed_attributes = allowed_attributes
        self.default_attribute = default_attribute
        self.default_order = default_order

    def modify(self, query: Query, params):
        """
        Sorts and orders the query by the sort_by and order_by param.

        If the sort_by param is not in the allowed attributes or the order_by param is
        not in the param, then the objects are sorted descending.
        """

        sort_by = params.get('sort-by', self.default_attribute)
        order_by = params.get('order-by', self.default_order)

        if sort_by not in self.allowed_attributes:
            return query

        if order_by is None:
            return query

        # gets the column of the object to sort by
        attribute = getattr(self.model, sort_by)
        
        if order_by == 'desc':
            return query.order_by(attribute.desc())

        return query.order_by(attribute)


class ByColumn(Modifier):
    """
    A modifier class for only getting objects that have a specific value in a attribute.

    :param model: The model to get from.
    :param param_name: The name of the param to get the value of the column from.
    :param attribute: The name of the column to get the object by.
    :param converter: A callable to convert the user submitted value to something different.
    """

    def __init__(self, model, param_name: str, attribute: str, converter: t.Callable=None):
        self.model = model
        self.param_name = param_name
        self.attribute = attribute
        self.converter = converter


    def modify(self, query: Query, params):
        """
        Modifies the query to only have object where a attribute is equal to a value.

        If the param name is not present, the unmodified query is returned. If the converter
        returns an error while converting, the query is returned.
        """

        attr_value = params.get(self.param_name)

        if attr_value is None or attr_value == '':
            return query
        
        if self.converter is not None:
            try:
                column_value = self.converter(attr_value)
            except ValueError:
                return query

        attribute = getattr(self.model, self.attribute)

        return query.where((attribute == attr_value) | (attribute == ''))


class SearchableAttribute:
    """
    A searchable attribute for the SearchInAttributes Modifier.

    The check_contains function should take a model, attribute name, and the search.
    
    :param name: The name of the attribute.
    :param check_contains: A function to check if the attribute contains the search.
    :param models: A list of models to join when searching.
    """

    def __init__(self, name: str, check_contains: t.Callable=None, models=[]):
        self.name = name
        self.check_contains = check_contains
        self.models = models
        
    def contains(self, model, data: str):
        """Check if the attribute contains the data."""
        if self.check_contains is None:
            return getattr(model, self.name).contains(data)

        return self.check_contains(model, self.name, data)


class SearchInAttributes(Modifier):
    """
    A modifier class for searching in attributes.

    The user can choose what attributes to search in with a comman separated list
    in the 'search_in' kwargs. The search keywords go in the 'k' param.

    :param model: The model to search in.
    :param allowed_attributes: The attributes the user can search in.
    :param default_attribute: The attribute to search in by default.
    """

    def __init__(self, model, searchable_attributes, default_attribute):
        self.model = model
        self.searchable_attributes = searchable_attributes
        self.default_attribute = default_attribute

    def modify(self, query: Query, param):
        """
        Modifies the query to only contain objects that match the search query.

        If the search query param is not present, the unmodified query is returned. If no
        usable attributes are found in the search_in param, the default attribute is used.
        """

        keywords = param.get('k')
        search_in = param.get('search-in', self.default_attribute)

        if keywords is None:
            return query

        search_in_attribute_names = search_in.split(',')
        search_in_attributes = []
        
        for name in search_in_attribute_names:
            name = name.strip()
            search_in_attributes.extend([attr for attr in self.searchable_attributes if attr.name == name])

        if search_in_attributes == []:
            search_in_attributes = [default_attribute]

        for attr in search_in_attributes:
            for model in attr.models:
                query = query.join(model)

        keywords = keywords.split()
        for keyword in keywords:
            query = query.where(
                reduce(lambda a, b: a | b, [attr.contains(self.model, keyword) for attr in search_in_attributes])
            )

        return query


class BySupportedDistro(Modifier):
    """
    A modifier class for getting by supported distros.

    This only works on App and Script object. This is becuase the SupportedDistro object only
    contains backrefs to App and Script. It looks in the 'supports' param for the distro. The
    'supports' param can contain multiple distros seporated by commas.
    """
    
    def modify(self, query: Query, params):
        """
        Modifies the query to only contain objects that support a specific distro.

        If the 'supports' param is not present or contains a unsupported distro, the unmodified query is
        returned.
        """

        # gets the supported distros of the object to get.
        supports = params.get('supports')

        if supports is None or supports == '':
            return query
        
        supported_distros = {}
        for distro in supports.split(','):
            distro = distro.split(':')
            distro_name = distro[0].strip()
            if len(distro) > 1:
                architectures = distro[1:]
            else:
                supported_distros[distro_name] = ['*']
                continue

            supported_distros[distro_name] = (arch.strip() for arch in architectures)

        if supported_distros == {}:
            return query

        if query.model == App:
            query = query.join(Script)
        
        query = (
            query
            .join(ScriptData)
            .join(SupportedDistrosJunction)
            .join(SupportedDistro)
        )

        for distro in supported_distros.keys():
            for arch in supported_distros[distro]:
                query = query.where(
                    reduce(
                        lambda a, b: a & b,
                        [(((SupportedDistro.distro_name == distro) | (SupportedDistro.distro_name == '*')) if distro != '*' else True) & (((SupportedDistro.architecture_name == arch) | (SupportedDistro.architecture_name == '*')) if arch != '*' else True)]
                    )
                )

        return query


class Paginate(Modifier):
    """
    A modifier class for paginating groups of objects.

    :param default_per_page: The default amount of objects per page.
    :param max_per_page: The maximium objects per page.
    """

    def __init__(self, default_per_page: int, max_per_page: int):
        self.default_per_page = default_per_page
        self.max_per_page = max_per_page

    def modify(self, query: Query, params):
        """
        Modifies the query to only show object on the page.

        It if the 'page' param is not present, then it defualts to the first. If the 'per-page'
        param is not present, then it defaults to the default amount.
        """
        try:
            page = int(params.get('page', 1))
        except ValueError:
            page = 1
        try:
            per_page = int(params.get('per-page', self.default_per_page))
        except ValueError:
            per_page = self.default_per_page

        if per_page > self.max_per_page:
            per_page = max_per_page

        return query.paginate(page, per_page)


class BySupportedAction(Modifier):
    """"
    A modifier class for getting by supported actions.

    This only works on Script objects. It uses the 'actions' param in the url.
    """

    def modify(self, query: Query, params):
        if 'actions' not in params.keys():
            return query
        
        actions = [action.strip() for action in params['actions'].split(',')]

        query = query.join(ScriptData).join(Action)
        
        for action in actions:
            query = query.where(
                Action.name.contains(action)
            )

        return query


class BySupportedShell(Modifier):
    """"
    A modifier class for getting by shell.

    This only works on Script objects. It uses the 'shell' param in the url.
    """

    def modify(self, query: Query, params):
        if 'shell' not in params.keys():
            return query

        query = query.join(ScriptData).join(Shell)
        
        query = query.where(
            Shell.name.contains(params['shell'])
        )

        return query
