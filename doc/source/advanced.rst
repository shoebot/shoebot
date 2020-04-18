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


Running in Jupyter
------------------

`Jupyter notebooks <https://jupyter.org>_` are fantastic, and Shoebot runs pretty well inside them!

First, you need to have Jupyter installed, as well as the development version
of Shoebot. Using ``virtualenvwrapper`` for this is heavily recommended.

.. code-block:: bash

    # create the virtualenv
    mkvirtualenv jupytershoebot -p $(which python3)
    # install jupyter dependencies
    pip3 install jupyter jupyter-pip
    # clone the Shoebot repository, enter it and install
    git clone https://github.com/shoebot/shoebot
    cd shoebot
    python3 setup.py install

After ensuring both packages are available, install the extension after cloning
the `jupyter-shoebot <https://github.com/shoebot/jupyter-shoebot/>`_ repository:

.. code-block:: bash

    # leave the shoebot/ dir
    cd ..
    # clone the jupyter-shoebot repository, enter it and install
    git clone https://github.com/shoebot/jupyter-shoebot
    cd jupyter-shoebot
    python3 setup.py install

And finally, while still on the ``jupyter-shoebot/`` directory, run

.. code-block:: bash

    jupyter kernelspec install shoebot_kernel --sys-prefix

All done! Now you can run ``jupyter notebook``, go to the ``Kernel`` menu, select
``Change kernel`` and select ``Shoebot``.

Be sure to try the `notebook examples <https://github.com/shoebot/jupyter-shoebot/tree/master/example-notebooks>_`
in the Jupyter Shoebot repository.


Running with PyPy
-----------------

To get better performance, you can run Shoebot using PyPy3, which is experimental. 

When installing Shoebot, you have to point to PyPy3 when creating your virtualenv. Instead of the first command in the :ref:`Virtualenvwrapper install example <virtualenvwrapper-install>`, do:

.. code:: bash

    mkvirtualenv shoebot -p $(which pypy3)

For the plain virtualenv approach, try:

.. code:: bash

    virtualenv .env -p $(which pypy3)


Using with Django
-----------------

See the `shoebot-django <https://github.com/stuaxo/shoebot-django>`_ for an example of integrating Shoebot into a Django application.

