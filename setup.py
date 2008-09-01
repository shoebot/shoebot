#!/usr/bin/env python

from distutils.core import setup

setup(name = "shoebot",
      version = "0.2",
      description = "A vector graphics scripting application",
      author = "ricardo lafuente",
      author_email = "r@sollec.org",
      license = 'GPL v3',
      url = "http://shoebot.sollec.org",
      packages = ["shoebot",
                  ],
      data_files = [("share/shoebot/examples", ["examples/primitives.bot",
                                  "examples/socketcontrol.pd",
                                        "examples/socketcontrol.bot",
                                        "examples/socketcontrol2.bot",
                                  ])
                    ],
      scripts = ["sbot"],
      long_description = """
Shoebot is a Python application for vector scripting.
It implements some shortcuts around the intricacies of Cairo,
and can also run external scripts and quickly generate image
outputs, as well as operating in realtime in windowed (GTK) mode.
"""
)

