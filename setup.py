#!/usr/bin/env python

from distutils.core import setup

setup(name = "shoebot",
      version = "0.2",
      description = "Shoebot - a Pythonic vector graphics scripting application",
      author = "ricardo lafuente",
      author_email = "r@sollec.org",
      license = 'GPL v3',
      url = "http://shoebot.sollec.org",
      packages = ["shoebot",
                  ],
      data_files = [("share/examples", ["examples/primitives.py",
                                        "examples/socketcontrol.pd",
                                        "examples/socketcontrol.py",
                                        "examples/socketcontrol2.py",
                                        ])
                    ],
      scripts = ["sbox"],
      long_description = """
Shoebot is a runtime for reading Nodebox source files. It
implements Nodebox's domain-specific language through Cairo.
"""
)

