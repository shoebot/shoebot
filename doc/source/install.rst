============
Installation
============
Shoebot runs on Python 3.7 and above.

GNU/Linux
---------

Installing dependencies
^^^^^^^^^^^^^^^^^^^^^^^

You need a few software packages on your system before installing Shoebot.
You can either run the handy ``./install/install_dependencies.sh`` script, or
paste the command relevant to your distribution from the list below.

Debian and Ubuntu:

.. code:: bash

  sudo apt install build-essential gir1.2-gtk-3.0 gir1.2-rsvg-2.0 \
  gobject-introspection libgirepository1.0-dev libglib2.0-dev \
  libgtksourceview-3.0-dev libjpeg-dev libpango1.0-dev python3-dev python3-gi \
  python3-gi-cairo python3-wrapt

Arch and Manjaro:

.. code:: bash

  pacman -S cairo gobject-introspection gobject-introspection-runtime gtk3 \
  gtksourceview3 libjpeg-turbo librsvg pango python python-cairo python-gobject \
  python3-wrapt

Fedora and CentOS:

.. code:: bash

  sudo yum install cairo-gobject redhat-rpm-config gcc cairo-devel \
  libjpeg-devel python3-devel python3-gobject python3-wrapt

SuSE:

.. code:: bash

  sudo zypper install gcc libjpeg62-devel python-gobject python-gobject-cairo \
  python3-wrapt

Installing Shoebot
^^^^^^^^^^^^^^^^^^

It is recommended to install Shoebot locally, although it can be also be
installed system-wide with ``sudo``.

.. code:: bash

    python3 setup.py install

.. _virtualenvwrapper-install:

If you prefer using virtual environments, we recommend using `virtualenvwrapper
<https://virtualenvwrapper.readthedocs.org/en/latest/>`_. These are the steps:

.. code:: bash

    mkvirtualenv shoebot -p $(which python3)
    python3 setup.py install

To run Shoebot in the future, you will need to activate the environment first
with ``workon shoebot``.


Mac OS X
--------

Installation on Mac OS X is identical to GNU/Linux based distributions.

Dependencies can be installed with the `install_dependencies.sh` script mentioned above,
or by running:

.. code:: bash

  pip3 install wrapt --user
  brew install cairo gobject-introspection gtk+3 gtksourceview3 jpeg libffi \
    librsvg py3cairo pygobject3


Windows
-------

Shoebot will install and run on Windows 64-bit (7 and above) using `msys2
<https://www.msys2.org/>`_.

The necessary dependencies can be installed by downloading and running the
`install_dependencies.sh
<https://raw.githubusercontent.com/shoebot/shoebot/master/install/install_dependencies.sh>`_
script. Save this file to your ``Msys2 home\user`` directory (the default is
``C:\msys64\home\%YourUserName%\``), run ``Msys2 Sys`` from the Start Menu and
enter:

.. code:: bash

  ./install_dependencies.sh

When that is complete, enter:

.. code:: bash

  git clone https://github.com/shoebot/shoebot

When that is done, run ``MinGW 64-bit`` from the Start Menu and enter:

.. code:: bash

  cd shoebot
  python setup.py install

After installing, the compiled executables can be used without running the Msys2
shell.


Trouble?
--------

Installation is the trickiest step in Shoebot, and can be more challenging than
we'd like. If you run into install problems, check the :doc:`troubleshooting page <troubleshooting>`.
