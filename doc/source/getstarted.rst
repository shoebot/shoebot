===============
Getting Started
===============

Running an example script
-------------------------

To get started, clone the Shoebot repository and head over to the `examples/` directory. Once you're there, try running:

.. code:: bash

    sbot grid/balls.bot

If everything went well with your installation, a window should open with an image.

Shoebot reads scripts written in the Nodebox language and translates them into images or animations.

You can right click anywhere on the image window to view the output in full screen or export it as an image or vector file.

Headless operation
------------------

There is also a mode where the result is directly rendered into an image or vector file, without a window. We can do this with the ``-o`` option, short for ``--outputfile``:

.. code:: bash

    sbot grid/balls.bot -o balls.png

This will create the ``balls.png`` image file. You can also create SVG, PDF and PostScript (``.ps``) files.

For a list of extra options, there's always ``--help`` or ``-h``.

.. code:: bash

    sbot --help
