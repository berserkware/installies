import bcrypt
import string
import random
import string

from datetime import date

def gen_salt():
    """Generates a salt via bcrypt."""

    return bcrypt.gensalt()

def hash_password(password: str) -> str:
    """Hashes a password using bycrypt."""

    # Hashes the text
    byte_pass = password.encode('utf8')
    salt = gen_salt()

    password = bcrypt.hashpw(byte_pass, salt)
    return password.decode('utf8')
    
def make_token():
    """
    Creates a 50 letter long string of random letters and numbers,
    Returns the string.
    """

    letters = string.ascii_lowercase + string.ascii_uppercase + '1234567890'
    return ''.join(random.choice(letters) for i in range(50))
    
def create_account_data(username, email, password) -> str:
    """Creates the account data to be put in a database"""
    
    # Gets the date
    today = date.today()
    
    # creates the token
    token = make_token()

    return (username, password, email, today, token, 0, )