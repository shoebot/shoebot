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
    mkvirtualenv jupytershoebot
    # install jupyter dependencies
    pip install jupyter jupyter-pip
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

To get better performance, you can run Shoebot using PyPy, which is experimental. 

When installing Shoebot, you have to point to PyPy when creating your virtualenv. Instead of the first command in the :ref:`Virtualenvwrapper install example <virtualenvwrapper-install>`, do:

.. code:: bash

    mkvirtualenv shoebot -p `which pypy`

For the plain virtualenv approach, try:

.. code:: bash

    virtualenv .env -p `which pypy`


Using with Django
-----------------

See the `shoebot-django <https://github.com/stuaxo/shoebot-django>`_ for an example of integrating Shoebot into a Django application.

Shoebox Virtual Machine
-----------------------

Shoebox is a ready-to-use VirtualBox image that we use for Shoebot workshops. It's a lightweight Xubuntu-based system, with some components stripped for size. Shoebot and its Gedit plugin are installed and working out of the box.

It is the easiest way to get non-GNU/Linux systems running Shoebot. Even for GNU/Linux systems, it's the best choice if you don't want to add yet another package to your system, but aren't comfortable with virtualenvs.

To try this, `Download VirtualBox <https://virtualbox.org/wiki/Downloads>`_, and then get the `Shoebox appliance file <https://mega.co.nz/#!B15lxKAZ!xLqAvVzIVV6BvBmBHZhlDJGkxHLx5yhfYC_z246Fy94>`_ (1.5 GB), import it into VirtualBox through ``File > Import Appliance``, and launch your new Shoebox.

