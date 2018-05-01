Developing
==========

This section is for anyone who is interested in contributing to the codebase, or knowing more about the internals. 


Coding style
------------

This is an adaptation of the indications proposed in PEP8 for a consistent Python coding style.

We try to have Shoebot examples follow this specification. Here are some of the principles that we like to follow.

* Indent with **4 spaces**, no tabs.
* Maximum **79 characters per line**.
* Comments are in **English**.
* Variables and functions are in ``lowercase`` and ``underscored_lowercase``, class names are in ``CamelCase``.

Be sure to read the full `PEP8 specification <http://legacy.python.org/dev/peps/pep-0008/>`_. When in doubt, be bold!


Making a release
----------------

This is our checklist to be sure we don't miss any detail when we put out a release.

  * update the version number in these files:
    - Makefile
    - setup.py
    - doc/source/conf.py
    - shoebot/gui/ide.py

  * update the changelogs
    - CHANGELOG
    - debian/changelog

  * tag the release commit
  * publish release on GitHub

  * push to PyPI

Building Debian packages
------------------------

There are some dependencies to look out for::

    sudo apt-get install rename dh-python cdbs

Be sure to go through this checklist:

  * update the debian/changelog file
