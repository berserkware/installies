from installies.database.models import App, User
from installies.lib.url import make_slug
from datetime import date
from peewee import *

def get_distros_from_string(distros: str):
    """
    Get a list of distros from a comma separated list.

    :param distros: A comma separated list of distros.
    """
    # puts the supported distros into a list
    script_supported_distros = distros.split(',')

    # strips the distros of spaces
    striped_distros = []
    for distro in script_supported_distros:
        if distro != '':
            striped_distros.append(distro.strip())

    return striped_distros

def create_app(name: str, description: str, author_id: int) -> App:
    """
    Creates an App object.

    :param name: The name of the app.
    :param description: The app description.
    :param author_id: The id of the author of the script.
    """

    # creates a slug out of the name of the script
    slug = make_slug(name)

    # gets the creation date of the app
    creation_date = date.today()

    author = User.get(User.id == author_id)

    app = App(
        name=name,
        slug=slug,
        description=description,
        creation_date=creation_date,
        author=author
    )

    return app
