import os

from peewee import MySQLDatabase
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = os.path.join(Path(__file__).parent.resolve(), '.env')
load_dotenv(dotenv_path)
os.environ['TZ'] = 'UTC'

database = MySQLDatabase(
    os.environ.get('DATABASE_NAME'),
    user=os.environ.get('DATABASE_USER'),
    password=os.environ.get('DATABASE_PASS'),
    host=os.environ.get('DATABASE_HOST'),
    port=int(os.environ.get('DATABASE_PORT'))
)

apps_path = os.environ.get('SCRIPT_UPLOAD_PATH')

max_script_length = os.environ.get('MAX_SCRIPT_LEN', 10000)

noreply_email = os.environ.get('NOREPLY_EMAIL')
noreply_email_password = os.environ.get('NOREPLY_EMAIL_PASSWORD')
smtp_server = os.environ.get('SMTP_SERVER')
smtp_server_port = int(os.environ.get('SMTP_SERVER_PORT'))
