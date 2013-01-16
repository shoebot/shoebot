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

The quickest way is to use the init_bot function, it sets up an appropriate
canvas and lets us draw to it.

.. code-block:: python

    bot = shoebot.initbot(outputfile="output.svg")
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
TODO
