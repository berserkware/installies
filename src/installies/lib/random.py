import random

def gen_random_id() -> str:
    """Generates a random 5 digit long number."""

    nums ='1234567890'
    return ''.join(random.choice(nums) for i in range(5))