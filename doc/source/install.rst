============
Installation
============

GNU/Linux
---------

Shoebot runs on Python 2.7.

You need a few software packages on your system before installing Shoebot. There is a small handy script that will take care of this for you:

.. code:: bash

    cd install
    ./install_dependencies.sh

Now, the simplest way to install Shoebot is system-wide, but you can also install it locally with a few extra steps. This has the advantage of keeping your base system intact.


If the script does not support your operating system, skip to `Add support for another operating system`.

System-wide install
^^^^^^^^^^^^^^^^^^^

Only one command necessary:

.. code:: bash

    sudo python setup.py install


.. _virtualenvwrapper-install:

Local install using virtualenvwrapper
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you're using the handy `virtualenvwrapper <https://virtualenvwrapper.readthedocs.org/en/latest/>`_, these are the necessary commands:

.. code:: bash

    mkvirtualenv shoebot
    python setup.py install

To use Shoebot in the future, you will need to activate the environment first:

.. code:: bash

    workon shoebot

Local install using a plain virtualenv
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you don't use virtualenvwrapper, run these commands after installing the dependencies.

.. code:: bash

    virtualenv .env
    source .env/bin/activate
    python setup.py install

To use shoebot in the future, remember to activate the environment first.

.. code:: bash

    source .env/bin/activate


Mac OS X
--------

Installation on Mac OS X should work the same by following the above instructions.

It is however poorly tested, since the developers of Shoebot are focusing on GNU/Linux; if you run into any unexpected issue, let us know in the `issue tracker <https://github.com/shoebot/shoebot/issues>`_.

Windows
-------

Windows is currently untested. There used to be a purpose-built Windows version of Shoebot (Spryte) but it has been unmaintained for a long while.

If you try your hand at running Shoebot on Windows and can get *anything* running, let us know in our `issue tracker`_ so we can improve this documentation.


Add support for another operating system
----------------------------------------

To add support for another OS you will need to install the libraries that Shoebot depends on:

Core:

.. code::

    Python2 Pycairo Pygobject Pango

GUI:

.. code::

    Gtk3

The community for your operating system may be able to offer help here.

Check progress with diagnose
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Shoebot provides a `diagnose` command as part of setup to check if things are working.


.. code:: bash

    python setup.py diagnose


It's usually easiest to start with Python and Pycairo, then move on to Pango and Gtk3.


PGI with CairoCFFI and Gtk3
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Shoebot can run under PGI and CairoCFFI, which may be easier to install than the recommened setup with pygobject and cairo.

In this setup Shoebot can work with the GUI, but text output is not available.


Open a bug on the Shoebot issue tracker
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Open a bug on the issue tracker to track progress on adding your OS.

https://github.com/shoebot/shoebot/issues
