#!/usr/bin/env python3
import gi

gi.require_version("PangoCairo", "1.0")
from gi.repository import PangoCairo


def list_pango_fonts():
    """Returns a list of available Pango font names. Names are returned in the
    Pango font string format, e.g. "Inconsolata Bold"."""
    names = []
    families = PangoCairo.font_map_get_default().list_families()
    for family in families:
        # in Inconsolata Bold, Inconsolata is the family, and Bold is the face
        facenames = [
            f"{family.get_name()} {face.get_face_name()}"
            for face in family.list_faces()
        ]
        names.extend(facenames)
        # this is how to access a font's FontDescription, which will help if
        # or when we want to get more info from font files
        # description = face.describe()
    return names


if __name__ == "__main__":
    print(list_pango_fonts())
