from peewee import Query

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
    :param allowed_columns: The columns that the objects can be sorted by.
    :param default_column: The column that the objects are softed by by default.
    :param default_order: The order that the objects are ordered by by default.
    """

    def __init__(self, model, allowed_columns, default_column, default_order='asc'):
        self.model = model
        self.allowed_columns = allowed_columns
        self.default_column = default_column
        self.default_order = default_order

    def modify(self, query: Query, **kwargs):
        """
        Sorts and orders the query by the sort_by and order_by kwargs.

        If the sort_by kwarg is not present, then the objects are sorted descending.
        """

        sort_by = kwargs.get('sort_by', self.default_column)
        order_by = kwargs.get('order_by', self.default_order)

        if sort_by not in self.allowed_columns:
            return query

        # gets the column of the object to sort by
        column = getattr(self.model, sort_by)
        
        if order_by == 'desc':
            return query.order_by(column.desc())

        return query.order_by(column)


class ByDatabaseColumn(Modifier):
    """
    A modifier class for only getting objects that have a specific value in a column.

    :param model: The model to get from.
    :param kwarg_name: The name of the kwarg to get the value of the column from.
    :param column: The column to get the object by.
    :param converter: A callable to convert the user submitted value to something different.
    """

    def __init__(self, model, kwarg_name: str, column, converter: t.Callable=None):
        self.model = model
        self.kwarg_name = kwarg_name
        self.column = column
        self.converter = converted


    def modify(self, query: Query, **kwargs):
        """
        Modifies the query to only have object where a column is equal to a value.

        If the kwarg name is not present, an empty list is returned.
        """

        column_value = kwargs.get(self.kwarg_name)

        if column_value is None:
            return []
        
        if self.converter is not None:
            column_value = self.converter(column_value)

        return query.where(self.column == column_value)
