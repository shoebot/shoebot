***************
Getting Started
***************

[TODO: 
- explain the language with some example scripts.
- how to edit scripts with a GUI (Gedit)  
]


Command-line usage
------------------

Using the Shoebot console runner is straightforward:

    sbot hypnoval.bot

This command will run the ``hypnoval.bot`` script, and create an output image
file -- the default filename is ``output.svg``). You can find many example Shoebot scripts inside the `examples` dir.

You'll probably want to specify your own output file name:

    sbot inputfile.bot -o image.png

The allowed extensions for the output filename are ``.svg``, ``.ps``, ``.pdf`` and ``.png``.

Shoebot can also run in a window, which is useful for quick previews, as well
as realtime manipulation of parameters. For this, just use the ``--window`` flag or ``-w``:

    sbot -w inputfile.bot

For a list of extra options, there's always ``--help`` or ``-h``.

    sbot -h
