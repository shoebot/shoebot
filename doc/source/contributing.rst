============
Contributing
============

Non-development tasks
=====================

Help improve our documentation
------------------------------

We're missing a few details and we'd definitely welcome some help here!

Port Nodebox library pages
^^^^^^^^^^^^^^^^^^^^^^^^^^

Most of the pages in the :doc:`libraries section <libraries>` are stubs. While the
original Nodebox documentation is good enough reference, it's becoming important
to port those docs over to the Shoebot manual because most of the images are
missing on the Nodebox site. (The `PlotDevice manual
<https://plotdevice.io/manual>`_ thankfully keeps its own adaptation.)

It's not hard to adapt the Nodebox docs to the Shoebot manual: docs are written
in the ReStructured Text format (a kind of souped-up Markdown), and you can take
a look at the `source of the colors library page
</_sources/libraries/colors.rst.txt>`_ for an example of what Sphinx files look
like. This `cheat sheet <https://matplotlib.org/sampledoc/cheatsheet.html>`_
explains the basics. From there, you can help complete the stub pages, which
would be just excellent.

Report errors or missing parts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Pointing out parts that are missing or wrong is a great way to help. If you spot
something, file an issue  with the ``documentation`` label on the issue tracker
to help us on this, or just pop over on the `Matrix channel
<https://matrix.to/#/#shoebot:matrix.org>`_.

Development tasks
=================

Make new examples or port existing ones
---------------------------------------

We're always eager to welcome new examples that explain a concept or show off an
interesting technique.

You can either contribute your own examples, or help port existing scripts:

* the `nodebox-pyobjc examples
  <https://github.com/karstenw/nodebox-pyobjc/tree/master/examples>`_, which are
  more current than those in the old Nodebox 1 repository

* the scripts in the `Nodebox gallery
  <https://www.nodebox.net/code/index.php/Gallery>`_

They should work mostly without modifications -- we need help testing them. Try
them out and post any issues you find on our `issue tracker
<https://github.com/shoebot/shoebot/issues/>`_ in case you hit a wall.

Be sure to also check the brief guidelines in :ref:`example-style` so that your
efforts can be included in Shoebot.


Help port libraries
-------------------

We're missing a few Nodebox libraries; can you help us port them to Shoebot?

See the full list of :ref:`unported-libs`.

Incidentally, we're also missing documentation to explain how to port Nodebox
libraries. If you're interested but stuck, file an issue and we'll help you.


Add support for another operating system
----------------------------------------

We support a few operating systems, but we'd like to expand the list.

To add support for another OS, you just need to find out its package names for
the libraries that Shoebot depends on:

- Python 3
- Pycairo
- PyGObject3
- Pango
- Pillow
- GTK3 (for the windowed canvas)
- GTKSourceView3 (for the IDE)

The community for your operating system may be able to offer help here. The
`install_dependencies.sh <https://github.com/shoebot/shoebot/blob/master/install/install_dependencies.sh>`_
script might help too.


Look for 'Help Out' issues
--------------------------

The `issues tagged 'Help Out'
<https://github.com/shoebot/shoebot/issues?q=is%3Aopen+is%3Aissue+label%3A%22help+out%22>`_
don't need a deep knowledge of Shoebot internals, and there's a good variety of
tasks to be done.


Make text editor plugins
------------------------

While our simple editor is around, power-users will be using their favourite
text editor to hack on Shoebot scripts.  Having plugins for any popular text
editor would be a fantastic addition.


Integrate Shoebot with other software
-------------------------------------

Shoebot can be a great tool to complement other software, be it for

- SVG, PDF or bitmap generation
- simple visualizations
- interact in real-time with the socket server

If you see a use case where Shoebot could be helpful, we'll do our best to
support you in implementing it.


Tips for Developers
===================

Coding style for the Shoebot core code
--------------------------------------

We follow the `PEP8 style guidelines
<https://www.python.org/dev/peps/pep-0008/>`_ additionally
`pre-commit <https://pre-commit.com/>` automates further linting and formatting on commit.

Install `pre-commit <https://pre-commit.com/>`

    ``pip install pre-commit``

Now, on every commit the following plugins will run:

docformatter: to format docstrings.
flynt: updates legacy string formatting.

.. _example-style:

Coding style for examples
-------------------------

When creating examples for including in Shoebot, we try to adhere to a set
of writing guidelines to make it easy for newcomers to understand what's going
on.

* Avoid one-letter variables (other than ``x`` and ``y``), and avoid
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

    - ``Makefile``
    - ``VERSION``
    - ``doc/source/conf.py``
    - ``shoebot/ide/ide.py``

  * update the changelogs

    - ``CHANGELOG``
    - ``debian/changelog``

  * tag the release commit
  * publish release on GitHub
  * push to PyPI

    - register on PyPI and place your credentials in ``~/.pypirc``
    - install Twine
    - make a source build with ``python setup.py sdist``
    - make a test upload to TestPyPI with ``twine upload --repository-url https://test.pypi.org/legacy/ dist/shoebot-1.3.tar.gz``
    - if all is good, upload to PyPI with ``twine upload dist/shoebot-1.3.tar.gz``
    - be sure to change the version numbers in the previous commands according to the current Shoebot version

Building Debian packages
------------------------

There are some dependencies to look out for::

    sudo apt-get install rename dh-python cdbs

Be sure to go through this checklist:

  * update the debian/changelog file

Then, generate the Debian packages with the `make builddeb` command.
