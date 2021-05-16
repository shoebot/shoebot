===============
Getting Started
===============

For your first time with Shoebot, you can try out the included code editor by
running ``shoebot`` in your terminal.

Open one of the example scripts and Run it through the `Run -> Run script` menu
option or the ``Ctrl-R`` keyboard shortcut. A window should open with an image
or animation.

You can now start editing the code and re-running to see the new outcome.
Changing values on example scripts is a great way to understand how things work.

The Shoebot code editor is however rather limited. We recommend trying out Atom
with the :ref:`Shoebot extension <atom>` for a more powerful and customizable
coding environment.


Running in the console
----------------------

If you prefer using your own text editor to edit files and just want something
to run the scripts, the `sbot` command is what you want. Head over to the
``examples/`` directory and try running:

.. code:: bash

    sbot grid/balls.bot

By default, Shoebot will open a window with the result. But we can also
output directly to a file with the ``-o`` option, short for ``--outputfile``.
Supported formats are SVG, PNG, PDF and PS.

.. code:: bash

    sbot grid/balls.bot -o balls.svg

There are many features available in the console runner that aren't accessible
in the Shoebot or Atom editors, so be sure to take a look at the :doc:`Command
line flags<cli_flags>` section.

Exporting video
---------------
