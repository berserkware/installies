from peewee import *

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