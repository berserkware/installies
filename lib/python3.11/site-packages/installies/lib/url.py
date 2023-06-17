def make_slug(string: str) -> str:
    """
    Turns a string in to a slug. 
    E.g 'String Thing' -> 'string-thing'
    
    :param string: The string to slugify.
    """

    lower = string.lower()
    slug = lower.replace(' ', '-')
    return slug