===============
Troubleshooting
===============

Here you'll find help with some common problems. If your problem isn't listed,
feel free to `file an issue <https://github.com/shoebot/shoebot/issues/new>`_
including your error message and the output of ``python setup.py diagnose``. You
can also join us on the Shoebot `Matrix channel
<https://matrix.to/#/#shoebot:matrix.org>`_.

Installation issues
-------------------

Check progress with diagnose
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you're having trouble with a specific package, Shoebot provides a 'diagnose'
command to check if things are working: ``python3 setup.py diagnose``

It's usually easiest to start with Python3 and Pycairo, then move on to
PyGobject, Pango and Gtk3.


Try PGI with CairoCFFI and GTK3 instead of PyGobject and Pycairo
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Shoebot can run under PGI and CairoCFFI, which may be easier to install
than the recommended setup with Pygobject and Pycairo.

In this setup Shoebot can work with the GUI, but text output is not available.


Other problems
--------------

TypeError: Couldn't find foreign struct converter for 'cairo.Context'
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you see this error, it means you're missing the Python GObject interface for
cairo. On Debian/Ubuntu, this should be fixed with:

.. code-block:: bash

    sudo apt-get install python3-gi-cairo

See the :doc:`installation page <install>` to know the relevant dependencies in
other distros.

The Gedit plugin does not activate
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Try running Gedit from the command line so that you can see debug messages. If
you see one of these warnings:

.. code-block:: bash

    ** (gedit:3830): WARNING **: Could not load Gedit repository: Typelib file for namespace 'GtkSource', version '3.0' not found

or:

.. code-block:: bash

    ImportError: cannot import name Gedit

then try installing the ``gir1.2-gtksource-3.0`` package.

`This StackOverflow answer <http://askubuntu.com/a/414592>`_ helped on finding
this solution. 
