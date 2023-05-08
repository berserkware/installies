from peewee import Query
from installies.apps.app_manager.models import Distro, SupportedDistro

import typing as t

class Modifier:
    """
    A base class for modifying Query objects with user submitted params.

    This class defines the standard for all modifier classes to follow.
    """

    def modify(self, query: Query, **kwargs):
        """
        A method for modifying SelectQuerys.

        It should take a query, modify it with the kwargs, and return it.
        """

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

    def modify(self, query: Query, **kwargs):
        """
        Sorts and orders the query by the sort_by and order_by kwargs.

        If the sort_by kwarg is not in the allowed attributes or the order_by kwarg is
        not in the kwargs, then the objects are sorted descending.
        """

        sort_by = kwargs.get('sort_by', self.default_attribute)
        order_by = kwargs.get('order_by', self.default_order)

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
    :param kwarg_name: The name of the kwarg to get the value of the column from.
    :param attribute: The name of the column to get the object by.
    :param converter: A callable to convert the user submitted value to something different.
    """

    def __init__(self, model, kwarg_name: str, attribute: str, converter: t.Callable=None):
        self.model = model
        self.kwarg_name = kwarg_name
        self.attribute = attribute
        self.converter = converter


    def modify(self, query: Query, **kwargs):
        """
        Modifies the query to only have object where a attribute is equal to a value.

        If the kwarg name is not present, the unmodified query is returned. If the converter
        returns an error while converting, the query is returned.
        """

        attr_value = kwargs.get(self.kwarg_name)

        if attr_value is None:
            return query
        
        if self.converter is not None:
            try:
                column_value = self.converter(attr_value)
            except ValueError:
                return query

        attribute = getattr(self.model, self.attribute)

        return query.where(attribute == attr_value)


class SearchInAttributes(Modifier):
    """
    A modifier class for searching in attributes.

    The user can choose what attributes to search in with a comman separated list
    in the 'search_in' kwargs. The search string goes in the 'q' kwargs.

    :param model: The model to search in.
    :param allowed_attributes: The attributes the user can search in.
    :param default_attribute: The attribute to search in by default.
    """

    def __init__(self, model, allowed_attributes, default_attribute):
        self.model = model
        self.allowed_attributes = allowed_attributes
        self.default_attribute = default_attribute

    def modify(self, query: Query, **kwargs):
        """
        Modifies the query to only contain objects that match the search query.

        If the search query kwarg is not present, the unmodified query is returned. If no
        usable attributes are found in the search_in kwarg, the default attribute is used.
        """

        search_query = kwargs.get('q')
        search_in = kwargs.get('search_in', self.default_attribute)

        if search_query is None:
            return query

        search_in_attribute_names = search_in.split(',')
        search_in_attributes = []
        
        for name in search_in_attribute_names:
            name = name.strip()
            if name in self.allowed_attributes:
                search_in_attributes.append(getattr(self.model, name))

        if search_in_attributes == []:
            search_in_attributes = [getattr(self.model, self.default_attribute)]

        for attr in search_in_attributes:
            query = query.where(attr.contains(search_query))

        return query


class BySupportedDistro(Modifier):
    """
    A modifier class for getting by supported distros.

    This only works on App and Script object. This is becuase the SupportedDistro object only
    contains backrefs to App and Script. It looks in the 'supports' kwarg for the distro.
    """

    def modify(self, query: Query, **kwargs):
        """
        Modifies the query to only contain objects that support a specific distro.

        If the 'supports' kwarg is not present or contains a unsupported distro, the unmodified query is
        returned.
        """

        # gets the supported distros of the object to get.
        supports = kwargs.get('supports')

        #gets the supported Distro object
        distro = Distro.select().where(Distro.slug == supports)

        if distro.exists() is False:
            return query

        distro = distro.get()

        query = query.join(SupportedDistro).join(Distro)

        return query.filter(Distro.id == distro.id)
