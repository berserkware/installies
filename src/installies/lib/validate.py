
class Validator:
    """
    A base class for validating user submitted data.

    Validation is done using checker classes that you can add to the
    ``checkers`` list attribute. The checkers should have a ``check`` method
    that should take a string, which is the data to check. The checkers should
    raise a ``ValueError`` if the data is not valid. The ValueError should
    contain a message suitable for returning to the user. The message
    should contain curly braces to be formatted with the name of the
    data. The name of the data should be put in the ``data_name``
    attribute of the validator. The data name is defaulted to "Data"
    """

    # An empty list for the checker functions
    checkers = []

    # A string containing the default data name
    data_name = 'Data'

    @classmethod
    def validate(cls, data: str):
        """
        Validate a string argument.

        An error will be raised if the data is not valid. None is
        is returned if the data is valid. It uses the checker classes
        in the ``checkers`` list attribute.

        :param data: The data to check.
        """
        checkers = cls.checkers

        for checker in checkers:
            try:
                checker.check(data)
            except ValueError as e:
                new_message = str(e).format(cls.data_name)
                raise ValueError(new_message)
