from textwrap import dedent

COLOR_CONVERSIONS = {}


def format_to_format_docstring(src, dest):
    """
    Generate a docstring for a color conversion function.

    :param src: Source format
    :param dest: Destination format
    """
    return dedent(f"""\
            Convert a color from {src.upper()} format to {dest.upper()} format.

            Parameters:
            color (tuple): A tuple of color values in {src.upper()} format, each component in the range [0, 1].

            Returns:
            tuple: Corresponding color values in {dest.upper()} format, each component in the range [0, 1].
        """)


def register_converter(func):
    name_parts = func.__name__.split('_to_')
    assert len(name_parts) == 2, "Function name must be in the format 'src_to_dest'"
    src, dest = name_parts

    assert (src, dest) not in COLOR_CONVERSIONS, f"{src}_to_{dest} already registered."
    COLOR_CONVERSIONS[(src, dest)] = func

    if not func.__doc__:
        func.__doc__ = format_to_format_docstring(src, dest)

    return func


@register_converter
def rgb_to_hsv(rgb):
    """
    Convert an RGB color to HSV.

    Parameters:
    rgb (tuple): A tuple of (r, g, b) where each component is in the range [0, 1].

    Returns:
    tuple: Corresponding HSV values as (h, s, v), each in the range [0, 1].
    """
    if any(not (0.0 <= component <= 1.0) for component in rgb):
        raise ValueError("RGB components must be in the range [0, 1]")

    r, g, b = rgb
    maxc = max(r, g, b)
    minc = min(r, g, b)
    v = maxc

    if minc == maxc:
        return 0.0, 0.0, v

    s = (maxc - minc) / maxc
    rc = (maxc - r) / (maxc - minc)
    gc = (maxc - g) / (maxc - minc)
    bc = (maxc - b) / (maxc - minc)

    if r == maxc:
        h = bc - gc
    elif g == maxc:
        h = 2.0 + rc - bc
    else:
        h = 4.0 + gc - rc

    h = (h / 6.0) % 1.0
    return h, s, v


@register_converter
def hsv_to_rgb(hsv):
    """
    Convert an HSV color to RGB.

    Parameters:
    hsv (tuple): A tuple of (h, s, v) where h (hue) is in the range [0, 1],
    and s (saturation) and v (value) are in the range [0, 1].

    Returns:
    tuple: Corresponding RGB values as (r, g, b), each in the range [0, 1].
    """
    h, s, v = hsv
    if not (0.0 <= h <= 1.0 and 0.0 <= s <= 1.0 and 0.0 <= v <= 1.0):
        raise ValueError("HSV components must be in the range [0, 1]")

    if s == 0.0:
        return v, v, v

    h_i = int(h * 6)
    f = (h * 6) - h_i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)

    if h_i == 0:
        return v, t, p
    if h_i == 1:
        return q, v, p
    if h_i == 2:
        return p, v, t
    if h_i == 3:
        return p, q, v
    if h_i == 4:
        return t, p, v
    if h_i == 5:
        return v, p, q
    # Considering the possibility of floating-point imprecision
    return v, t, p


@register_converter
def rgb_to_rgba(rgb):
    """Convert RGB to RGBA adding an alpha channel set to 1.0."""
    return rgb + (1.0,)


@register_converter
def rgba_to_rgb(rgba):
    return rgba[:3]


def register_converter_to_rgb(func):
    """
    Register a color conversion function that converts to RGB format.

    Automatically also generates converters to RGBA and HSV formats.
    """
    src, dest = func.__name__.split('_to_')
    assert dest == 'rgb', "Destination format must be RGB"

    register_converter(func)

    def src_to_rgba(color):
        return rgb_to_rgba(func(color))

    def src_to_hsl(color):
        return rgb_to_hsl(func(color))

    def src_to_hsv(color):
        return rgb_to_hsv(func(color))

    src_to_rgba.__name__ = f'{src}_to_rgba'
    register_converter(src_to_rgba)

    src_to_hsl.__name__ = f'{src}_to_hsl'
    register_converter(src_to_hsl)

    src_to_hsv.__name__ = f'{src}_to_hsv'
    register_converter(src_to_hsv)


@register_converter
def hsv_to_rgba(hsv):
    return rgb_to_rgba(hsv_to_rgb(hsv))


@register_converter
def rgb_to_hsl(rgb):
    """
    Convert an RGB color to HSL.

    Parameters:
    rgb (tuple): A tuple of (r, g, b) where each component is in the range [0, 1].

    Returns:
    tuple: Corresponding HSL values as (h, s, l), each in the range [0, 1].
    """
    if any(not (0.0 <= component <= 1.0) for component in rgb):
        raise ValueError("RGB components must be in the range [0, 1]")

    r, g, b = rgb
    maxc = max(r, g, b)
    minc = min(r, g, b)
    l = (minc + maxc) / 2.0

    if minc == maxc:
        return 0.0, 0.0, l

    s = (maxc - minc) / (1 - abs(2 * l - 1))
    rc = (maxc - r) / (maxc - minc)
    gc = (maxc - g) / (maxc - minc)
    bc = (maxc - b) / (maxc - minc)

    if r == maxc:
        h = bc - gc
    elif g == maxc:
        h = 2.0 + rc - bc
    else:
        h = 4.0 + gc - rc

    h = (h / 6.0) % 1.0
    return h, s, l


@register_converter
def rgba_to_hsl(rgba):
    return rgb_to_hsl(rgba_to_rgb(rgba))


def register_converter_from_rgb(func):
    """
    Register a color conversion function that converts from RGB format.

    Automatically also generates converters from RGBA and HSV formats.
    """
    src, dest = func.__name__.split('_to_')
    assert src == 'rgb', "Source format must be RGB"

    register_converter(func)

    def rgba_to_dest(rgba):
        return rgba_to_rgb(func(rgba))

    def hsl_to_dest(hsl):
        return hsl_to_rgb(func(hsl))

    def hsv_to_dest(hsv):
        return hsv_to_rgb(func(hsv))

    rgba_to_dest.__name__ = f'rgba_to_{dest}'
    register_converter(rgba_to_dest)

    hsl_to_dest.__name__ = f'hsl_to_{dest}'
    register_converter(hsl_to_dest)

    hsv_to_dest.__name__ = f'hsv_to_{dest}'
    register_converter(hsv_to_dest)


@register_converter_to_rgb
def hsl_to_rgb(hsl):
    """
    Convert an HSL color to RGB.

    Parameters:
    hsl (tuple): A tuple of (h, s, l) where h (hue) is in the range [0, 1],
    and s (saturation) and l (lightness) are in the range [0, 1].

    Returns:
    tuple: Corresponding RGB values as (r, g, b), each in the range [0, 1].
    """
    h, s, l = hsl
    if not (0.0 <= h <= 1.0 and 0.0 <= s <= 1.0 and 0.0 <= l <= 1.0):
        raise ValueError("HSL components must be in the range [0, 1]")

    if s == 0.0:
        return l, l, l

    h_i = int(h * 6)
    f = (h * 6) - h_i
    p = l * (1 - s)
    q = l * (1 - f * s)
    t = l * (1 - (1 - f) * s)

    if h_i == 0:
        return l, t, p
    if h_i == 1:
        return q, l, p
    if h_i == 2:
        return p, l, t
    if h_i == 3:
        return p, q, l
    if h_i == 4:
        return t, p, l
    if h_i == 5:
        return l, p, q
    # Considering the possibility of floating-point imprecision
    return l, t, p


@register_converter_to_rgb
def v_to_rgb(v):
    return v, v, v


@register_converter
def va_to_rgba(va):
    return va[0], va[0], va[0], va[1]


@register_converter_from_rgb
def rgb_to_v(rgb):
    return sum(rgb) / 3.0


@register_converter
def rgba_to_va(rgba):
    return *rgb_to_v(rgba[:3]), rgba[3]

@register_converter
def rgb_to_hex(rgba, prefixed=True):
    if prefixed:
        prefix = '#'
    else:
        prefix = ''
    return (prefix + '%02x%02x%02x') % tuple(int(c*255) for c in rgba[:3])
