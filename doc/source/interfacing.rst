Interfacing with the outside world
==================================

Shoebot is not limited to what you write inside your .bot file; you can open
your sketch for receiving and reacting to data from outside applications and
environments.

Live variables
--------------

These can be set from the commandline using JSON syntax:

    $ sbot -w --vars='{ "hue": 32 }' examples/basic/var_number_hsb.bot

You can also set these values from the socketserver (see below),
or running the live shell.


Using the live variables GUI
----------------------------

When a script uses the `var` keyword, the corresponding widget will appear in
the live variables GUI.

The following code will make a slider with a minimum value of 0, a maximum
value of 100, and an initial (default) value of 25.

.. code-block:: python

        var('a_number', NUMBER, 25., 0., 100.)

.. figure::  images/live_vars.png

Socketserver
------------

If shoebot is run with the `--serverport` option, a socket server will also be
started. Socket servers can accept connections from other applications or even
across the network in order to set variables inside Shoebot scripts. The
default socket server port is 7777.

    $ sbot -ws -p examples/animation/hypnoval.bot
    Listening on port 7777...

Once it's running, it's easy to connect with telnet:

    $ telnet 127.0.0.1 7777

This gets you into the shell, where you can use the commands below to list and
set variables, rewind and go to frames. 

The following commands can also be sent through other applications like Pure
Data; there is a simple PD example in `examples/socketcontrol/helloworld.pd`.

Be sure to take a look at the socket server examples in action inside the
`examples/socketserver` directory.


Socketserver commands
---------------------


    Playback Commands

    ==================   ======================================
    Command              Description
    ==================   ======================================
    goto 100             Go to frame 100
    pause                pause playback
    rewind               set FRAME to 0
    restart              set FRAME to 0 and reset all variables
    ==================   ======================================

    Using variables

    ==================   ======================================
    Command              Description
    ==================   ======================================
    vars                 Show content of all Shoebot Variables
    set n=1              set variable 'n' to value 1
    n=1                  set variable 'n' to value 1
    ==================   ======================================


    Other

    ==================   ======================================
    Command              Description
    ==================   ======================================
    help                 Show list of all commands
    ==================   ======================================




Live coding: Editors/IDEs and the live shell
--------------------------------------------

Shoebot provides a live shell for communication with text editors.

All the socket server commands above are available, as well as `load_base64`
which allows livecoding.

To experiment with the livecoding shell, run an example with the -l option

    $ sbot -wl examples/animation/hypnoval.bot

This has all the commands that the socket server has, and extra commands
that can be useful for an editor or IDE.


Live Shell commands
-------------------

    Live Shell Commands

    ==================   ==============================================
    Command              Description
    ==================   ==============================================
    quit                 quit shoebot
    load_base64          used by IDE/Editor to send new code to Shoebot
    ==================   ==============================================



Embedding
---------

For applications that use standard image formats, like the web it is enough to use
create_bot and output image formats (see 'using shoebot as a module').



Pure Data
---------






