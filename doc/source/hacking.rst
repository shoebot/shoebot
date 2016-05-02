Hacking Shoebot
===============

This section is for the Python hackers who want to get dirty with canvas manipulation and so on.

Using Shoebot as a Python module
--------------------------------

Shoebot can also be loaded as a module. For now, scripts taking advantage of
this must be placed inside the shoebot dir.

After including an import statement,

.. code-block:: python

    import shoebot

a NodeBot object needs to be created, and all further drawing commands can be 
called on that instance.

The quickest way is to use the create_bot function, it sets up an appropriate
canvas and lets us draw to it.

.. code-block:: python

    bot = shoebot.create_bot(outputfile="output.svg")
    bot.size(400,400)
    bot.rect(10,10,100,100)

When you're finished with drawing, just call

.. code-block:: python

    bot.finish()

and your output file should be created.

Also, you can save snapshots of the current state if the Bot instance like so:

.. code-block:: python

    bot.snapshot("snap.png")

You can even call external Shoebot/Nodebox scripts from your Python script:

.. code-block:: python

    bot.run("example.bot")


Working directly with Cairo
---------------------------
TODO

Command-line usage
------------------

Enter sbot -h to see available options, they are split into logical groups:

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

