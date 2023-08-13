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
from installies.lib.url import make_slug

class ReportTitleValidator(Validator):
    """A class for validating report title."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=64),
        AllowedCharactersChecker(
            allow_extra=['-', ',', '.', '"', '\'', '(', ')'],
        )
    ]
    
    data_name = 'Report title'


class ReportBodyValidator(Validator):
    """A class for validating report body."""

    checkers = [
        EmptyChecker(),
        LengthChecker(max_len=2048),
        AllowedCharactersChecker(
            allow_extra=['-', ',', '.', '"', '\'', '(', ')'],
        )
    ]

    data_name = 'Report body'
