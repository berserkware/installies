from installies.config import database
from installies.apps.app_manager.models import App, Script, Distro, SupportedDistro
from installies.apps.auth.models import User


def create_database():
    """Create tables in database."""
    with database:
        database.create_tables([User, App, Script, Distro, SupportedDistro])


def drop_database():
    """Drop tables in database."""
    with database:
        database.drop_tables([User, App, Script, Distro, SupportedDistro])


def recreate_database():
    """Drop and recreates the database tables."""
    drop_database()
    create_database()
