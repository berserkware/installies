import random
import string

def gen_random_id() -> str:
    """Generates a random 5 digit long number."""

    nums ='1234567890'
    return ''.join(random.choice(nums) for i in range(10))

def gen_random_string(length: int) -> str:
    """Generates a random string of characters and numbers of a specified length."""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))
