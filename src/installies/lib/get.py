class SortBy:
    """
    A getter class for sorting and ordering the objects by either ascending or descending.

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

    def get(self, objects, **kwargs):
        """
        Sorts and orders the objects by the sort_by and order_by kwargs.

        If the sort_by kwarg is not present, then the objects are sorted descending.
        """

        sort_by = kwargs.get('sort_by', self.default_column)
        order_by = kwargs.get('order_by', self.default_order)

        if sort_by not in self.allowed_columns:
            return objects

        # gets the column of the object to sort by
        column = getattr(self.model, sort_by)
        
        if order_by == 'desc':
            return objects.order_by(column.desc())

        return objects.order_by(column)
