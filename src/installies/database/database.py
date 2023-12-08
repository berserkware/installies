from installies.config import database
from installies.models.app import App
from installies.models.script import Script, AppScript, Action
from installies.models.supported_distros import SupportedDistro
from installies.models.user import User, Session, Ban, PasswordResetRequest
from installies.models.report import Report, ReportAppInfo, ReportScriptInfo, ReportCommentInfo
from installies.models.discussion import AppThread, Thread, Comment
from installies.models.maintainer import Maintainers, Maintainer
from installies.models.voting import VoteJunction, Vote

tables =  [
    User,
    Session,
    App,
    AppScript,
    Script,
    Ban,
    PasswordResetRequest,
    Action,
    SupportedDistro,
    Maintainer,
    Maintainers,
    Report,
    ReportAppInfo,
    ReportScriptInfo,
    ReportCommentInfo,
    Thread,
    AppThread,
    Comment,
    VoteJunction,
    Vote,
]

def create_database():
    """Create tables in database."""
    with database:
        database.create_tables(tables)


def drop_database():
    """Drop tables in database."""
    with database:
        database.drop_tables(tables)


def recreate_database():
    """Drop and recreates the database tables."""
    drop_database()
    create_database()
