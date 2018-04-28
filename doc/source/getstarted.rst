===============
Getting Started
===============

Running Shoebot in a window
---------------------------

To get started, clone the Shoebot repository and head over to the `examples/` directory. Once you're there, try running:

.. code:: bash

    sbot -w grid/balls.bot

If everything went well with your installation, a window should open with an image.

Shoebot reads scripts written in the Nodebox language and translates them into images. In this case, the `-w` option (short for ``--window``) displays the output in a window. You can also have the result output directly into a file if you omit the ``-w`` option:

.. code:: bash

    sbot grid/balls.bot -o balls.png

This will create the ``balls.png`` image file. You can also create SVG, PDF and PostScript (``.ps``) files.

For a list of extra options, there's always ``--help`` or ``-h``.

    sbot -h
