from installies.config import database
from installies.models.app import App
from installies.models.script import Script, ScriptData
from installies.models.supported_distros import Distro, SupportedDistro, Architecture, AlternativeArchitectureName
from installies.models.user import User
from installies.models.report import AppReport
from installies.models.discussion import Thread, Comment
from installies.models.maintainer import Maintainers, Maintainer

tables =  [
    User,
    App,
    ScriptData,
    Script,
    Distro,
    SupportedDistro,
    Maintainer,
    Maintainers,
    Architecture,
    AlternativeArchitectureName,
    AppReport,
    Thread,
    Comment,
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
