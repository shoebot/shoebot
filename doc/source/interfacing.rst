Interfacing with the outside world
==================================

Shoebot is not limited to what you write inside your .bot file; you can open your sketch for receiving and reacting to data from outside applications and environments.

Introducing live variables
--------------------------

These can be set from the commandline using JSON syntax,
--vars '{ "varname": value }'

$ sbot -w --vars='{ "hue": 32 }' examples/basic/var_number_hsb.bot

You can also set these values from the socketserver (see below),
or running the live shell.


Using the live variables GUI
----------------------------

When a script uses the var keyword, an element will appear in the live variables GUI.

The following code will make a slider from 0-100 starting at 25

.. code-block:: python

        var('a_number', NUMBER, 25., 0., 100.)
        # see how roundness affects the shape

.. figure::  images/live_vars.png

Socketserver
------------

If shoebot is run with  --serverport  shoebot will run a socketserver.

You can run one of the examples on the default port of 7777 like this:

$ sbot -ws -p examples/animation/hypnoval.bot
Listening on port 7777...

Once it's running it's easy to connect with telnet:

$ telnet 127.0.0.1 7777

As well as setting and listing variables in the variables window, you can
do things like go to a particular frame.

Enter help to see which commands are available.


Socket server eamples are available in  examples/socketserver


Editors/IDEs and the live shell
-------------------------------

Shoebot provides a live shell for communication with editors.

All the commands in the socketserver are available as well as load_base64
which allows livecoding.

To experiment with the livecoding shell, run an example with the -l option

$ sbot -wl examples/animation/hypnoval.bot

Enter help to see which commands are available.


Embedding
---------



Pure Data
---------
* There is an example of linking puredata with shoebot in  examples/socketcontrol/helloworld.pd






