===============
Getting Started
===============

Running an example script
-------------------------

For your first time with Shoebot, try out the included code editor by running

.. code:: bash

    shoebot

Open one of the example scripts and Run it through the `Run -> Run script` menu option or the ``Ctrl-R`` keyboard shortcut.

A window should open with an image.  Shoebot reads scripts written in the Nodebox language and translates them into images or animations.

You can right click anywhere on the image window to view the output in full screen or export it as an image or vector file.

Using the console runner
------------------------

If you prefer using your own text editor to edit files and just want something to run the scripts, the `sbot` command is what you want. Head over to the `examples/` directory and try running:

.. code:: bash

    sbot grid/balls.bot

Headless operation
------------------

There is also a mode where the result is directly rendered into an image or vector file, without a window. We can do this with the ``-o`` option, short for ``--outputfile``:

.. code:: bash

    sbot grid/balls.bot -o balls.png

This will skip the window view and create the ``balls.png`` image file. You can also create SVG, PDF and PostScript (``.ps``) files.

For a list of extra options, see the :doc:`cli_flags` section.
