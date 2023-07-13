def get_distros_from_string(distro_string: str):
    """
    Gets a dictonary of supported distros and their architectures.

    The distro string should be formatted as "distro1:arch1:arch2, distro2:arch1:arch2".

    :param distro_string: A comma separated list of distros.
    """
    strings = distro_string.split(',')

    distros = {}
    for string in strings:
        split_string = string.split(':')
        distro_name = split_string[0].strip()

        # adds to `distros` dict continues loop if there are no architectures
        if len(split_string) <= 1:
            distros[distro_name] = []
            continue

        architectures = []
        for i, value in enumerate(split_string):
            # skips the first element
            if i == 0:
                continue;

            architectures.append(value)

        distros[distro_name] = architectures

    return distros
            
        
