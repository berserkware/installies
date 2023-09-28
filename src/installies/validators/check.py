import string
import typing as t
import re

from peewee import DoesNotExist
from installies.validators.base import ValidationError

class EmptyChecker:
    """A checker class that checks if a string is empty."""

    def check(self, data: str, **kwargs):
        """
        Check if data string is empty.

        A ValidationError is raised if data is empty.

        :param data: The data to check.
        """
        if type(data) == str:
            data = data.strip()
        
        if data is None or data == '' or data == [] or data == {}:
            raise ValidationError(
                '{} cannot be empty.'
            )


class LengthChecker:
    """
    A class that checks the length of a string.

    :param max_len: The max length of the string.
    :param min_len: The minimium length of the string.
    """

    def __init__(self, max_len=None, min_len=None):
        self.max_len = max_len
        self.min_len = min_len

    def check(self, data: str, **kwargs):
        """
        Check the length of a data string.

        A ValidationError is raised if the data is too long or short.

        :param data: The data to check.
        """
        if self.max_len is not None and len(data) > self.max_len:
            raise ValidationError(
                '{} ' + f'must not contain more than {self.max_len} characters.'
            )

        if self.min_len is not None and len(data) < self.min_len:
            raise ValidationError(
                '{} ' + f'must contain at least {self.min_len} characters.'
            )


class CharacterWhitelistChecker:
    """
    A class that checks that a string only contains characters in a whitelist.

    :param allow_spaces: Allow spaces.
    :param allow_lowercase: Allow lowercase letters.
    :param allow_uppercase: Allow uppercase letters.
    :param allow_numbers: Allow numbers.
    :param allow_extra: A list of extra characters to allow.
    """

    def __init__(
        self,
        allow_spaces=True,
        allow_lowercase=True,
        allow_uppercase=True,
        allow_numbers=True,
        allow_extra=[]
    ):
        self.allowed_characters = []

        if allow_spaces:
            self.allowed_characters.extend(' ')

        if allow_lowercase:
            self.allowed_characters.extend(string.ascii_lowercase)

        if allow_uppercase:
            self.allowed_characters.extend(string.ascii_uppercase)

        if allow_numbers:
            self.allowed_characters.extend(string.digits)

        self.allowed_characters.extend(allow_extra)

    def check(self, data: str, **kwargs):
        """
        Check that only allowed characters in data string.

        Raises ValidationError if data contains characters that are not allowed.

        :param data: The data string to check.
        """
        for char in data:
            if char not in self.allowed_characters:
                raise ValidationError(
                    '{} ' + f'cannot contain character "{char}".'
                )


class CharacterBlacklistChecker:
    """
    A checker that checks that a string does not contain characters in a blacklist.

    :param disallowed_characters: The characters that are not allowed.
    """

    def __init__(self, disallowed_characters=[], **kwargs):
        self.disallowed_characters = disallowed_characters

    def check(self, data: str):
        """
        Check that no disallowed characters in data string.

        Raises ValidationError if data contains characters that are not allowed.

        :param data: The data string to check.
        """
        for char in data:
            if char in self.allowed_characters:
                raise ValidationError(
                    '{}' + f'cannot contain character "{char}".'
                )


class UniqueChecker:
    """
    A checker that checks that a string is unique in an column of a table.

    :param table: The table to check in.
    :param column_name: The name of the column to check in.
    :param data_modifier: A callable to modify the data before checking it in
        the database.
    """

    def __init__(
        self,
        table,
        column_name: str,
        data_modifier: t.Callable=None,
        query=None,
    ):
        self.table = table
        self.column_name = column_name
        self.data_modifier = data_modifier

    def check(self, data: str, **kwargs):
        """
        Check that data string does not exist in the database.

        A ValidationError is raised if the string exists in the database.

        :param data: The data string to check.
        """
        if self.data_modifier is not None:
            data = self.data_modifier(data)

        try:
            self.table.get(getattr(self.table, self.column_name) == data)
        except DoesNotExist:
            return

        raise ValidationError(
            '{} already exists.'
        )


class NotInContainerChecker:
    """
    A checker that checks that a string is in a container.

    :param container: The container to check that a string is in. The container can
        also be a callable to get a container.
    :param container_name: The name of the container the data needs to be in.
    """

    def __init__(self, container, container_name: str):
        self.container = container
        self.container_name = container_name

    def check(self, data: str, **kwargs):
        """
        Check that a data string exists in the the container.

        A ValidationError is raised if the string is not in the container.

        :param data: The data string to check.
        """
        
        container = self.container
        if callable(self.container):
            container = self.container()
        
        if data not in container:
            raise ValidationError('{} ' + f'must be in {self.container_name}.')


class InContainerChecker:
    """
    A checker that checks that a string is not in a container.

    :param container: The container to check that a string is not in. The container can
        also be a callable to get a container.
    :param container_name: The name of the container the data cannot be in.
    """

    def __init__(self, container, container_name: str):
        self.container = container
        self.container_name = container_name

    def check(self, data: str, **kwargs):
        """
        Check that a data string does not exist in the container.

        A ValidationError is raised if the string is in the container.

        :param data: The data string to check.
        """
        
        container = self.container
        if callable(self.container):
            container = self.container()
        
        if data in container:
            raise ValidationError('{} ' + f'must not be in {self.container_name}.')


class EmailChecker:
    """
    A checker that checks that the inputed data is an email.
    """

    def check(self, data: str, **kwargs):
        if not re.match('[^@]+@[^@]+\.[^@]+', data):
            raise ValidationError(f'{data} is not a valid email address.')


class DictionaryChecker:
    """
    A checker to check the key and values of dictionarys.

    :param key_validator: A validator to check the keys.
    :param value_validator: A validator to check the value.
    """

    def __init__(self, key_validator, value_validator):
        self.key_validator = key_validator
        self.value_validator = value_validator

    def check(self, data: dict, **kwargs):
        for key in data.keys():
            self.key_validator.validate(key)

        for value in data.values():
            if type(value) == list or type(value) == tuple:
                self.value_validator.validate_many(value)
            else:
                self.value_validator.validate(value)
        
