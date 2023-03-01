
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
    def check_data(cls, data: str, checker):
        """
        Check a piece of data against a checker class.

        :param data: The data to check.
        :param checker: The checking class to check the data.
        """
        try:
            checker.check(data)
        except ValueError as e:
            new_message = str(e).format(cls.data_name)
            raise ValueError(new_message)

    @classmethod
    def validate_many(cls, data: list):
        """
        Validates a list of data.

        An error will be raised if the data is not valid. None is
        is returned if the data is valid. It uses the checker classes
        in the ``checkers`` list attribute. If the data is a list then
        all the elements in the list will be checked.

        :param data: A list of data to check.
        """
        checkers = cls.checkers

        for checker in checkers:
            for item in data:
                cls.check_data(item, checker)

    @classmethod
    def validate(cls, data):
        """
        Validate a string or list argument.

        An error will be raised if the data is not valid. None is
        is returned if the data is valid. It uses the checker classes
        in the ``checkers`` list attribute. If the data is a list then
        all the elements in the list will be checked.

        :param data: The data to check.
        """
        checkers = cls.checkers

        for checker in checkers:
            cls.check_data(data, checker)
