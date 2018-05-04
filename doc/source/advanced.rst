Advanced usage
==============

This section is aimed at Python dabblers and hackers who want to get into the
more involved features of Shoebot.

Using Shoebot as a Python module
--------------------------------

Shoebot can be easily loaded as a module inside a Python script.

.. code-block:: python

    import shoebot

    # set up a canvas
    bot = shoebot.create_bot(outputfile="output.svg")

    # size() needs to be called first
    bot.size(400,400)

    # now we can draw!
    bot.rect(10,10,100,100)

    # finish() should be called after all drawing commands
    bot.finish()

Take a snapshot of the current state:

.. code-block:: python

    bot.snapshot("snap.png")

Run a Shoebot/Nodebox script:

.. code-block:: python

    bot.run("example.bot")

Command-line usage
------------------

Enter `sbot -h` to see all the available options:

.. code:: text

    usage: usage: sbot [options] inputfile.bot [args] [-h] [-o FILE] [-s]
                                                      [-p SERVERPORT] [-v VARS]
                                                      [-ns NAMESPACE] [-l]
                                                      [-a SCRIPT_ARGS] [-r REPEAT]
                                                      [-g GRAMMAR] [-w] [-f]
                                                      [-t TITLE] [-c] [-dv] [-dt]
                                                      [-V]
                                                      script [script_args]

.. code:: text

    positional arguments:
      script                Shoebot / Nodebox script to run (filename or code)

    optional arguments:
      -h, --help            show this help message and exit


Input / Output:

.. code:: text

      -o FILE, --outputfile FILE
                            run script and output to image file (accepts .png .svg
                            .pdf and .ps extensions)
      -s, --socketserver    run a socket server for external control (will run the
                            script in windowed mode)
      -p SERVERPORT, --serverport SERVERPORT
                            set socketserver port to listen for connections
                            (default is 7777)
      -v VARS, --vars VARS  Initial variables, in JSON (Note: Single quotes
                            OUTSIDE, double INSIDE) --vars='{"variable1": 1}'
      -ns NAMESPACE, --namespace NAMESPACE
                            Initial namespace, in JSON (Note: Single quotes
                            OUTSIDE, double INSIDE) --namespace='{"variable1": 1}'
      -l, --l               Simple shell - for IDE interaction
      -a SCRIPT_ARGS, --args SCRIPT_ARGS
                            Pass to the bot
      script_args

Bot Lifecycle:

.. code:: text

      -r REPEAT, --repeat REPEAT
                            set number of iteration, multiple images will be
                            produced
      -g GRAMMAR, --grammar GRAMMAR
                            Select the bot grammar 'nodebox' (default) or
                            'drawbot' languages

Window Management:

.. code:: text

      -w, --window          run script in a GTK window
      -f, --fullscreen      run in fullscreen mode
      -t TITLE, --title TITLE
                            Set window title
      -c, --close           Close window after running bot (use with -r for
                            benchmarking)
      -dv, --disable-vars   disable the variables pane when in windowed mode.

Debugging / Dev flags:

.. code:: text

      -dt, --disable-background-thread
                            disable running bot code in background thread.
      -V, --verbose         Show internal shoebot error information in traceback


.. _shell-mode:

Shell mode
----------

When run with the ``-l`` option, ``sbot`` gives you a shell inside which to control the windowed script.


Shoebox Virtual Machine
-----------------------

Shoebox is a ready-to-use VirtualBox image that we use for Shoebot workshops. It's a lightweight Xubuntu-based system, with some components stripped for size. Shoebot and its Gedit plugin are installed and working out of the box.

It is the easiest way to get non-GNU/Linux systems running Shoebot. Even for GNU/Linux systems, it's the best choice if you don't want to add yet another package to your system, but aren't comfortable with virtualenvs.

To try this, `Download VirtualBox <https://virtualbox.org/wiki/Downloads>`_, and then get the `Shoebox appliance file <https://mega.co.nz/#!B15lxKAZ!xLqAvVzIVV6BvBmBHZhlDJGkxHLx5yhfYC_z246Fy94>`_ (1.5 GB), import it into VirtualBox through ``File > Import Appliance``, and launch your new Shoebox.


Using with Django
-----------------

See the `shoebot-django <https://github.com/stuaxo/shoebot-django>`_ for an example of integrating Shoebot into a Django application.
