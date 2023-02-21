from installies.globals import database
from installies.database.models import User, App, Script

def create_database():
    with database:
        database.create_tables([User, App, Script])