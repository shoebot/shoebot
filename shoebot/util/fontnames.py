#!/usr/bin/env python3
import gi

gi.require_version("PangoCairo", "1.0")
from gi.repository import PangoCairo

# https://developer.gnome.org/pygtk/stable/index.html


def fontnames():
    """Returns a list of available Pango font names. Names are returned in the
    Pango font string format, e.g. "Inconsolata Bold"."""
    names = []
    families = PangoCairo.font_map_get_default().list_families()
    for family in families:
        # FIXME: Ensure this is the correct way to make a font name
        facenames = [
            f"{family.get_name()} {face.get_face_name()}"
            for face in family.list_faces()
        ]
        names.extend(facenames)
        # description = face.describe()
    return names


if __name__ == "__main__":
    print(fontnames())
