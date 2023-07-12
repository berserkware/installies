def remove_value_from_dictionary(dictionary: dict, key: str):
    """Removes a value from a dictionary, and returns the dictionary."""
    if key in dictionary.keys():
        del dictionary[key]
    return dictionary


def join_dictionaries(*dicts, **kwargs):
    """Joins dictionaries. Also adds the other extra kwargs."""

    new_dictionary = {}
    for dictionary in dicts:
        new_dictionary = new_dictionary | dictionary

    new_dictionary = new_dictionary | kwargs

    return new_dictionary
