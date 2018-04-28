============
Installation
============

GNU/Linux
---------

Shoebot runs on Python 2.7. To get better performance, you can run it using PyPy, which is experimental.

You need a few software packages on your system before installing Shoebot. There is a small handy script that will take care of this for you::

    cd install
    ./install_dependencies.sh

Now, the simplest way to install Shoebot is system-wide, but you can also install it locally with a few extra steps. This has the advantage of keeping your base system intact.

System-wide install
^^^^^^^^^^^^^^^^^^^

Only one command necessary::

    sudo python setup.py install
    
Local install using virtualenvwrapper
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you're using the handy [virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/), these are the necessary commands::

    mkvirtualenv shoebot
    pip install -r requirements.txt
    python setup.py install

To use Shoebot in the future, you will need to activate the environment first::
    
    workon shoebot

In case you have PyPy installed, make sure to point to it when creating the virtualenv. Instead of the first command in the previous example, do::

    mkvirtualenv shoebot -p `which pypy`

Local install using a plain virtualenv
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you don't use virtualenvwrapper, run these commands after installing the dependencies.

    virtualenv .env
    source .env/bin/activate
    pip install -r requirements.txt
    python setup.py install

To use shoebot in the future, remember to activate the environment first.

    source .env/bin/activate

Like in the Virtualenvwrapper instructions, to take advantage of PyPy you need to create the Virtualenv pointing to it::

    virtualenv shoebot-env -p `which pypy`


Other systems
=============

Mac OS X
--------

TODO

Windows
-------

TODO
