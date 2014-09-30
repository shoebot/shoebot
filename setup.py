#!/usr/bin/env python2

# Shoebot setup script
#
# 'python setup.py install', or
# 'python setup.py --help' for more options

# the following libraries will not be installed

EXCLUDE_LIBS = ['lib/sbopencv', 'lib/sbopencv/blobs']

import os
from distutils.core import setup

for lib in EXCLUDE_LIBS:
    # get subdirs of excluded libs
    for root, dir, files in list(os.walk(lib))[1:]:
        EXCLUDE_LIBS.append(root)


# dir globbing approach taken from Mercurial's setup.py
datafiles = [(os.path.join('share/shoebot/', root) ,[os.path.join(root, file_)
for file_ in files]) for root,dir,files in os.walk('examples')]
datafiles.append(('share/pixmaps', ['assets/shoebot-ide.png']))
datafiles.append(('share/shoebot/data', ['assets/kant.xml']))
#as the IDE is non functional, I'm commenting this
#datafiles.append(('share/applications', ['assets/shoebot-ide.desktop']))

datafiles.extend([(os.path.join('share/shoebot/', root) ,[os.path.join(root, file_)
for file_ in files]) for root,dir,files in os.walk('locale')])

# include all libs EXCEPT the ones mentioned in EXCLUDE_LIBS
datafiles.extend([(os.path.join('share/shoebot/', root) ,[os.path.join(root, file_)
for file_ in files]) for root,dir,files in os.walk('lib') if root not in EXCLUDE_LIBS])

setup(name = "shoebot",
    version = "1.0b",
    description = "Vector graphics scripting application",
    author = "Ricardo Lafuente",
    author_email = "r@sollec.org",
    license = 'GPL v3',
    url = "http://shoebot.net",
    packages = ["shoebot", "shoebot.core", "shoebot.data", "shoebot.gui", "shoebot.grammar", "shoebot.grammar.nodebox-lib", "shoebot.grammar.nodebox-lib.nodebox", "shoebot.grammar.nodebox-lib.nodebox.graphics", "shoebot.grammar.nodebox-lib.nodebox.geo"],
    data_files = datafiles,
    scripts = ['sbot', 'sbot.cmd'] if os.name == 'nt' else ['sbot'],
    long_description = """
 Shoebot is a pure Python graphics robot: It takes a Python script as input,
 which describes a drawing process, and outputs a graphic in a common open
 standard format (SVG, PDF, PostScript, or PNG). It has a simple text editor
 GUI, and scripts can describe their own GUIs for controlling variables
 interactively. Being pure Python, it can also be used as a Python module,
 a plugin for Python-scriptable tools such as Inkscape, and run from the
 command line.

"""
)

