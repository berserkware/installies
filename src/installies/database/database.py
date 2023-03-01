from installies.config import database
from installies.database.models import User, App, Script


def create_database():
    """Create tables in database."""
    with database:
        database.create_tables([User, App, Script])


def drop_database():
    """Drop tables in database."""
    with database:
        database.drop_tables([User, App, Script])


def recreate_database():
    """Drop and recreates the database tables."""
    drop_database()
    create_database()
