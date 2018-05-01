import os


def make_readable_filename(fn):
    """
    Change filenames for display in the menu.
    """
    return os.path.splitext(fn)[0].replace('_', ' ').capitalize()
