Command-line options
====================

This is a list of all the flags you can specify to the ``sbot`` command-line runner.


.. data:: --outputfile <FILENAME>, -o <FILENAME>

   Run in headless mode, outputting the result directly to a file.

   Supported extensions are ``.png``, ``.svg``, ``.pdf`` and ``.ps``.


.. data:: --socketserver, -s

   Run a :ref:`socket server <socketserver>` for controlling live variables from
   other programs.


.. data:: --serverport <PORT>, -s <PORT>

   Set the socket server port to listen for connections (default is 7777).


.. data:: --vars <VARS>, -v <VARS>

  Initial live variables, in JSON format.

  Use single quotes **outside**, and double quotes **inside**, e.g.:
  ``--vars='{"variable1": 1}'``


.. data:: --namespace <NAMESPACE>, -ns <NAMESPACE>

  Initial namespace, in JSON format.

  Use single quotes **outside**, and double quotes **inside**, e.g.:
  ``--namespace='{"variable1": 1}'``

  TODO: Document the difference between --namespace and --vars


.. data:: --l, -l

   Open a shell to control the bot as it runs. See the :ref:`Shell mode
   <shell-mode>` documentation for the available commands.


.. data:: --repeat <TIMES>, -r <TIMES>

  Set number of iterations to run the script, producing multiple images.


.. data:: --window, -w

  Run the script in a GTK window (default).


.. data:: --fullscreen, -f

  Run the script in fullscreen mode.


.. data:: --title <TITLE>, -t <TITLE>

   Set the window title.


.. data:: --close, -c

   Close the window after running the script. Use with ``--repeat`` for
   benchmarking.


.. data:: --disable-vars, -dv

   Disable the variables pane when in windowed mode.


.. data:: --disable-background-thread, -dt

   Don't run code in a background thread. This option is only useful if running
   on OSX turns up issues.


.. data:: --verbose, -V

   Show internal error information in tracebacks.


.. data:: --args <ARGS>, -a <ARGS>

  Pass arguments to bot. [TODO: explain better]
