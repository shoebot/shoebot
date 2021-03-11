#!/usr/bin/env python3
import gi
gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo
# https://developer.gnome.org/pygtk/stable/index.html

def fontnames():
    fontstrings = []
    families = PangoCairo.font_map_get_default().list_families()

    for family in families:
        for face in family.list_faces():
            # FIXME: Ensure this is the correct way to make a font name
            fontstrings.append(family.get_name() + ' ' + face.get_face_name())
            # description = face.describe()

    return fontstrings
