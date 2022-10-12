# -*- coding: utf-8 -*-
import sys

# on_rtd is whether we are on readthedocs.org
import os

on_rtd = os.environ.get("READTHEDOCS", None) == "True"

if not on_rtd:  # only import and set the theme if we're building docs locally
    import sphinx_rtd_theme

    html_theme = "sphinx_rtd_theme"
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# otherwise, readthedocs.org uses their theme by default, so no need to specify it

# use mock modules to avoid gobject errors
# https://docs.readthedocs.io/en/stable/faq.html#i-get-import-errors-on-libraries-that-depend-on-c-modules
autodoc_mock_imports = ["gobject", "pygobject"]

# order autodoc entries as per the source
autodoc_member_order = "bysource"


# General configuration
# ---------------------

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ["sphinx.ext.autodoc", "sphinxcontrib.shoebot"]

# Add any paths that contain templates here, relative to this directory.
templates_path = [".templates"]

# The suffix of source filenames.
source_suffix = ".rst"

# The encoding of source files.
# source_encoding = 'utf-8'

# The master toctree document.
master_doc = "index"

# General information about the project.
project = u"Shoebot Manual"
import datetime

copyright = f"2007-{datetime.date.today().year} the Shoebot authors"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = "1.4"
# The full version, including alpha/beta/rc tags.
release = "1.4"

# List of directories, relative to source directory, that shouldn't be searched
# for source files.
exclude_trees = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"


# Options for HTML output
# -----------------------

# The style sheet to use for HTML and HTML Help pages. A file of that name
# must exist either in Sphinx' static/ path, or in one of the custom paths
# given in html_static_path.
html_style = "css/theme.css"

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
# html_logo = None

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
# html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["static"]

# Output file base name for HTML help builder.
htmlhelp_basename = "Shoebotdoc"


def setup(app):
    app.add_css_file("customise_rtd.css")
