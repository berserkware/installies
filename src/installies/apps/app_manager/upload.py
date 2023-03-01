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
