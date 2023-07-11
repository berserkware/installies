def remove_value_from_dictionary(dictionary: dict, key: str):
    """Removes a value from a dictionary, and returns the dictionary."""
    if key in dictionary.keys():
        del dictionary[key]
    return dictionary
