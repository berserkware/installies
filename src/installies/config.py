import os

from peewee import *
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = os.path.join(Path(__file__).parent.resolve(), '.env')
load_dotenv(dotenv_path)

test = os.environ.get('TEST')

database = MySQLDatabase(
    'Installies', 
    user='installies', 
    password='password', 
    host='localhost', 
    port=3306)

supported_distros = [
    'ubuntu',
    'arch',
    'manjaro',
    'debian',
    'gentoo',
    'mint',
    'fedora',
    'opensuse'
]

supported_script_actions = [
    'install',
    'remove'
]

apps_path = '/media/berserkware/Data/Code/Installies/apps/'
