import os
import configparser

from peewee import MySQLDatabase
from pathlib import Path

os.environ['TZ'] = 'UTC'

config = configparser.ConfigParser()
config.read('/etc/installies/config.ini')

# general config
default_config = config['DEFAULT']

host = default_config['Host']
port = int(default_config['Port'])
debug_mode = default_config['DebugMode']

# config related to database
database_config = config['database']

database = MySQLDatabase(
    database_config['Name'],
    user=database_config['User'],
    password=database_config['Passwd'],
    host=database_config['Host'],
    port=int(database_config['Port'])
)

# config related to scripts
script_config = config['script']

apps_path = script_config['UploadPath']
max_script_length = int(script_config['MaxLength'])


# config related to email
email_config = config['email']

noreply_email = email_config['User']
noreply_email_password = email_config['Passwd']
smtp_server = email_config['SMTPAddr']
smtp_server_port = int(email_config['SMTPPort'])
