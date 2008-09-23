#!/usr/bin/env python

from distutils.core import setup
import os

setup(name = "shoebot",
    version = "0.1",
    description = "A vector graphics scripting application",
    author = "Ricardo Lafuente",
    author_email = "r@sollec.org",
    license = 'GPL v3',
    url = "http://tinkerhouse.net/shoebot",
    packages = ["shoebot"],
    data_files = [('share/shoebot', ['icon.png']),
                    ("share/shoebot/examples", ["examples/primitives.bot", "examples/socketcontrol.pd", "examples/socketcontrol.bot", "examples/socketcontrol2.bot"]),
                #    ("share/shoebot/examples",
                #     [os.path.join(root, file_) for file_ in files])
                #  for root, dirs, files in os.walk('examples')
                    ],
      scripts = ["sbot", "shoebot-ide"],
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

