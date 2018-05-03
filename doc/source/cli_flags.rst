Command-line options
====================

This is a list of all the flags you can specify to the ``sbot`` command-line runner.


.. data:: --outputfile <FILENAME>, -o <FILENAME>

   Run in headless mode, outputting the result directly to a file. 

   Supported extensions are ``.png``, ``.svg``, ``.pdf`` and ``.ps``.


.. data:: --socketserver, -s

   Run a socket server for external variable control.


.. data:: --serverport <PORT>, -s <PORT>

   Set the socket server port to listen for connections (default is 7777).


.. data:: --vars <VARS>, -v <VARS>

  Initial variables, in JSON format.

  Use single quotes **outside**, and double quotes **inside**, e.g.: ``--vars='{"variable1": 1}'``

  
.. data:: --namespace <NAMESPACE>, -ns <NAMESPACE>

  Initial namespace, in JSON format.

  Use single quotes **outside**, and double quotes **inside**, e.g.: ``--namespace='{"variable1": 1}'``


.. data:: --args <ARGS>, -a <ARGS>

  Pass arguments to bot. [TODO: explain better]


.. data:: --l, -l

   Open a shell to control the bot as it runs. See the :ref:`Shell mode <shell-mode>` documentation for the available commands.


.. data:: --repeat <TIMES>, -r <TIMES>

  Set number of iterations to run the script, producing multiple images.


.. data:: --grammar <LANG>, -g <LANG>

  Select the language to use: ``nodebox`` (default) or ``drawbot``.  

  Note that Drawbot support is experimental.


.. data:: --window, -w

  Run the script in a GTK window (default).


.. data:: --fullscreen, -f

  Run the script in fullscreen mode.


.. data:: --title <TITLE>, -t <TITLE>

   Set the window title.


.. data:: --close, -c

   Close the window after running the script. Use with ``--repeat`` for benchmarking.


.. data:: --disable-vars, -dv

   Disable the variables pane when in windowed mode.


.. data:: --disable-background-thread, -dt

   Don't run code in a background thread.


.. data:: --verbose, -V

   Show internal error information in tracebacks.
