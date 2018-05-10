Developing
==========

This section is for anyone who is interested in contributing to the codebase, or knowing more about the internals. 


Coding style for the Shoebot core code
--------------------------------------

We're not picky here, other than following `PEP8 style guidelines
<https://www.python.org/dev/peps/pep-0008/>`_. We use `flake8
<https://pypi.org/project/flake8/>`_ extensions in our code editors to
keep us strict, and recommend it.

.. _example-style:

Coding style for examples
-------------------------

When creating examples for including in Shoebot, we try to adhere to a set
of writing guidelines to make it easy for newcomers to understand what's going
on.

* Do not use one-letter variables (other than ``x`` and ``y``), and avoid
  two-letter names as well (things like ``dx`` can be expanded to ``deltax``).
  It will look less compact, but really helps understanding what's going on.
* Start the example with a docstring specifying the title of the example,
  author info and some details about the script and its workings. If you
  want to format this text, use Markdown.
* Use Flake8 or similar linter plugin to find necessary style fixes.
* Comments in English.
* Variables and functions are in ``lowercase`` and ``underscored_lowercase``,
  class names are in ``CamelCase``.


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
