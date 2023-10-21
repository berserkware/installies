class Group:
    """
    A base class for defining the interface for groups.

    Groups are for getting object by params submitted by users. The
    derivitive classes should add a model attribute to the class that
    contains the table that the group gets.
    """

    model = None

    @classmethod
    def get(cls, params, query=None):
        """
        Gets the group of objects.

        :param params: The parameters submitted by the user to get the objects.
        :param query: A query to use instead of cls.model.select().
        """
        return cls.model.select()
