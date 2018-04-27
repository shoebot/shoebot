===============
Troubleshooting
===============

The Gedit plugin does not activate
----------------------------------

Try running Gedit from the command line so that you can see debug messages. If you see one of these warnings::

    ** (gedit:3830): WARNING **: Could not load Gedit repository: Typelib file for namespace 'GtkSource', version '3.0' not found

or::

    ImportError: cannot import name Gedit

then try installing the `gir1.2-gtksource-3.0` package::

    sudo apt-get install gir1.2-gtksource-3.0

`This StackOverflow answer <http://askubuntu.com/a/414592>`_ helped on finding this solution. However, if you see this::

   (gedit:6027): libpeas-WARNING **: Could not find loader 'python3' for plugin 'shoebotit'

It might be because you're using an outdated version of Gedit. We've found this issue on Gedit 3.4.x, and it disappeared after updating to version 3.8.


