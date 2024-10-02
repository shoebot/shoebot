def hex_to_ints(hex_color):
    """
    Convert a hex color code to a tuple of integers from 0-255.

    :param hex_color: RGB hex string of 3 or 6 digits, or RGBA hex string of 4 or 8 digits.
    :return: A tuple of integers representing the RGB or RGBA values.
    """
    hex_color = hex_color.removeprefix("#")

    if len(hex_color) in [3, 4]:
        hex_color = ''.join([c*2 for c in hex_color])
    else:
        assert len(hex_color) in [6, 8], "Unknown hex format."

    return tuple(int(hex_color[i:i + 2], 16) for i in range(0, len(hex_color), 2))

def normalize(scale = 1.0, *args):
    """
    Normalize a series of values given a scale.

    :param scale: The scale for normalization.
    :param args: Values to be normalized.
    :return: tuple of normalized values.
    """
    return tuple(arg / scale for arg in args)

def hex_to_floats(hex_color, scale=255.0):
    """
    Convert a hex color code to a tuple of floats, optionally normalizing them.

    :param hex_color: A string representing a hex color code.
    :param scale: The scale for normalization, defaults to 255.0 so the floats are between 0.0 and 1.0
    :return: A tuple of floats or integers representing the RGB or RGBA values.
    """
    ints = hex_to_ints(hex_color)
    return normalize(scale, *ints)