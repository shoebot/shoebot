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
    pip install -r requirements.txt
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
    pip install -r requirements.txt
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
