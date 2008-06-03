#!/usr/bin/env python

from distutils.core import setup

setup(name = "shoebox",
      version = "0.2",
      description = "Shoebox - a Pythonic vector graphics scripting application",
      author = "ricardo lafuente",
      author_email = "r@sollec.org",
      license = 'GPL v3',
      url = "http://shoebox.sollec.org",
      packages = ["shoebox",
                  ],
      data_files = [("examples", ["examples/primitives.py",
                                  "examples/socketcontrol.pd",
                                  "examples/socketcontrol.py",
                                  "examples/socketcontrol2.py",
                                  ])
                    ],
      scripts = ["sbox"],
      long_description = """
Shoebox is a runtime for reading Nodebox source files. It
implements Nodebox's domain-specific language through Cairo.
"""          
)    
      
