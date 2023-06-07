def get_other_architechture_names_from_string(names: str):
    """
    Gets the names from a comma seporated list.

    :param names: The string with the architechture names.
    """

    return [name.strip() for name in names.split(',')]
