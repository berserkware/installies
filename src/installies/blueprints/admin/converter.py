def get_other_architecture_names_from_string(names: str):
    """
    Gets the names from a comma seporated list.

    :param names: The string with the architecture names.
    """

    return [name.strip() for name in names.split(',')]
