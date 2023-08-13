from installies.validators.base import Validator
from installies.validators.check import (
    EmptyChecker,
    LengthChecker,
    AllowedCharactersChecker,
    DisallowedCharactersChecker,
    UniqueChecker,
    NotInContainerChecker,
    DictionaryChecker,
)
from installies.models.app import App
from installies.models.discussion import Thread, Comment
from installies.lib.url import make_slug
from installies.config import (
    max_script_length,
)

class ThreadTitleValidator(Validator):
    """A class for validating topic titles."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=128),
        AllowedCharactersChecker(
            allow_extra=['-', ',', '.', '"', '\'', '(', ')'],
        ),
        UniqueChecker(
            table=Thread,
            column_name='title',
        ),
    ]

    data_name = 'Thread title'


class CommentContentValidator(Validator):
    """A class for validating comment content."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=1024),
        AllowedCharactersChecker(
            allow_extra=['-', ',', '.', '"', '\'', '(', ')'],
        ),
    ]

    data_name = 'Comment content'
