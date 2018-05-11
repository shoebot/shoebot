Shoebot documentation
=====================

Shoebot is a tool to automate the process of drawing vector graphics using a minimal and easy-to-understand syntax. It is a rewrite of `Nodebox 1 <https://www.nodebox.net/code/index.php/Home>`_ by Frederik de Bleser and Tom de Smedt, with the purpose of having an equivalent tool in GNU/Linux systems. Nodebox 1 is itself based on `DrawBot <http://www.drawbot.com/>`_ by Just van Rossum. 

It follows a rich lineage of tools dedicated to generative creativity:

  * Design By Numbers
  * Processing
  * Scriptographer
  * Paper.js

For more about the nature of creative coding and generative design, be sure to read `The Nodebox 1 theoretical introduction <https://www.nodebox.net/code/index.php/Introduction>`_.

Purpose
-------

Shoebot is a useful tool for many use cases:

* creating generative and procedural works, either for screen or print output
* teaching code to non-developers by means of immediate visual feedback
* prototyping visualizations and design concepts
* automatically generating sets of vector images
* live-coding and real-time tweaking of animated graphics

Features
--------

Originally built as a GNU/Linux version of Nodebox 1, Shoebot comes with many batteries included:

* supports of most of Nodebox 1's functionality
* user-friendly code editor
* headless mode for quick execution without the GUI parts
* it can run on a window or output files in PDF, PNG, SVG or PS formats
* ability to tweak running scripts via a simple GUI, a socket server or a text-based shell
* also works as a Python module to work inside existing programs


Links
-----

* `Main site <https://shoebot.github.io>`_
* `GitHub repository <https://github.com/shoebot/shoebot>`_
* `Issue tracker <https://github.com/shoebot/shoebot/issues>`_


Related projects
----------------

* `Drawbot`_, the tool that started it all, by Just van Rossum from Letterror. It's now been reinvigorated with new features and experimental Python 3 support.
* `Nodebox 3 <http://nodebox.net/node>`_, the current node-based incarnation of Nodebox, running on Java.
* `Nodebox-pyobjc <https://github.com/karstenw/nodebox-pyobjc>`_, an active fork of Nodebox 1, maintained by Karsten Wolf.

* `Canvas.js <https://www.clips.uantwerpen.be/pages/pattern-canvas>`_ by Nodebox's co-author Tom de Smedt, allows you to create browser-based scenes and animations with JS and HTML5.
* `Rapydbox <http://salvatore.pythonanywhere.com/RapydBox/default/editor>`_ -- A JavaScript version of Nodebox, based on `RapydScript <https://github.com/atsepkov/RapydScript>`_.


----

.. toctree::
   :maxdepth: 2
   
   install
   getstarted
   tutorial
   live
   libraries
   examples
   advanced
   extensions
   troubleshooting
   commands
   cli_flags
   compatibility
   contributing
   developing
   

.. We won't be needing these for now
    Indices and tables
    ==================

    * :ref:`genindex`
    * :ref:`modindex`
    * :ref:`search`
