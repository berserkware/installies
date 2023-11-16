from installies.config import host, port, protocol, hostname

def make_slug(string: str) -> str:
    """
    Turns a string in to a slug. 
    E.g 'String Thing' -> 'string-thing'
    
    :param string: The string to slugify.
    """

    lower = string.lower()
    slug = lower.replace(' ', '-')
    return slug

def get_base_url() -> str:
    """
    Gets the base url to installies based on the config.

    Examples: https://installies.org, http://0.0.0.0:8000, http://yourhostname.org:5000.
    """
    return f'{protocol}://{(hostname if hostname is not None else host)}{(f":{port}" if port != 80 else "")}'

    
