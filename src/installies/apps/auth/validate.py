from installies.lib.validate import Validator
from installies.lib.check import (
    EmptyChecker,
    LengthChecker,
    AllowedCharactersChecker,
    ExistsInDatabaseChecker,
)
from installies.database.models import User


class UsernameValidator(Validator):
    """A class for validating usernames submitted by users."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=32),
        AllowedCharactersChecker(
            allow_extra=['-', '_', '<', '>', '!']
        ),
        ExistsInDatabaseChecker(table=User, column_name='username'),
    ]

    data_name = 'Username'


class EmailValidator(Validator):
    """A class for validating passwords submitted by users."""

    checkers = [
        EmptyChecker(),
        ExistsInDatabaseChecker(User, 'email'),
    ]

    data_name = 'Email'


class PasswordValidator(Validator):
    """A class for validating passwords submitted by users."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=32)
    ]

    data_name = 'Password'


class PasswordConfirmValidator(Validator):
    """A class for validating password confirms submitted by users."""

    checkers = [
        EmptyChecker(),
    ]

    data_name = 'Password Confirm'
