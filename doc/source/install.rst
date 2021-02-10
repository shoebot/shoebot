============
Installation
============

GNU/Linux
---------

Shoebot runs on Python 3.7 and above.

You need a few software packages on your system before installing Shoebot. There is a small handy script that will take care of this for you:

.. code:: bash

    ./install/install_dependencies.sh

It is recommended to install Shoebot locally, although it can be also be installed system-wide.


If the script does not support your operating system, skip to `Add support for another operating system`.

Local install
^^^^^^^^^^^^^

Installing shoebot for the current user.

.. code:: bash

    python3 setup.py install


.. _virtualenvwrapper-install:

Local install using virtualenvwrapper
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you're using the handy `virtualenvwrapper <https://virtualenvwrapper.readthedocs.org/en/latest/>`_, these are the necessary commands:

.. code:: bash

    mkvirtualenv shoebot -p $(which python3)
    python3 setup.py install

To use Shoebot in the future, you will need to activate the environment first:

.. code:: bash

    workon shoebot

Local install using a plain virtualenv
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you don't use virtualenvwrapper, run these commands after installing the dependencies.

.. code:: bash

    virtualenv .env
    source .env/bin/activate
    python3 setup.py install

To use shoebot in the future, remember to activate the environment first.

.. code:: bash

    source .env/bin/activate

System wide install
-------------------

.. code:: bash

    sudo python3 setup.py install


Mac OS X
--------

Installation on Mac OS X is identical to GNU/Linux based distributions. 

Dependencies are installed via `Homebrew <https://brew.sh/>`_ through the
``install/install_dependencies.sh`` script.

Python 3.8 is supported on Homebrew, since that is what is currently
supported by pygobject3 there.


Windows
-------

Shoebot will install and run on Windows 64 bit (7 and above) using `msys2 <https://www.msys2.org/>`_. 

The easiest way to install Shoebot on Windows after installing Msys2 is to download and use the `install_dependencies.sh <https://raw.githubusercontent.com/shoebot/shoebot/master/install/install_dependencies.sh>`_ file.

Save this file to your ``Msys2 home\user`` directory (default ``C:\msys64\home\%YourUserName%\``).

Run ``Msys2 Sys`` from the Start Menu and enter:

.. code:: 

    ./install_dependencies.sh
	
When that is complete enter:

.. code::

    git clone https://github.com/shoebot/shoebot
	
When that is complete run ``MinGW 64-bit`` from the Start Menu and enter: 

.. code::

   	cd shoebot
	
	python setup.py install

After installing, the compiled executables can be used without running the Msys2 shell.


Add support for another operating system
----------------------------------------

To add support for another OS you will need to install the libraries that Shoebot depends on:

Core:

.. code::

    Python3 Pycairo PyGObject3 Pango Pillow

GUI:

.. code::

    GTK3 GTKsourceview3

The community for your operating system may be able to offer help here.
Looking at how the `install_dependencies.sh` script works for may help.


Check progress with diagnose
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Shoebot provides a `diagnose` command as part of setup to check if things are working.


.. code:: bash

    python3 setup.py diagnose


It's usually easiest to start with Python3 and Pycairo, then move on to PyGobject, Pango and Gtk3.


PGI with CairoCFFI and GTK3
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Shoebot can run under PGI and CairoCFFI, which may be easier to install
than the recommened setup with pygobject and cairo.

In this setup Shoebot can work with the GUI, but text output is not available.


Open a bug on the Shoebot issue tracker
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Open a bug on the issue tracker to track progress on adding your OS.

https://github.com/shoebot/shoebot/issues

