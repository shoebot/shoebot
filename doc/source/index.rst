Shoebot
=======

Shoebot is a tool to automate the process of drawing vector graphics using a minimal and easy-to-understand syntax.

It is a rewrite of `Nodebox 1 <https://www.nodebox.net/code/index.php/Home>`_ by `Frederik de Bleser <https://www.enigmeta.com/>`_ and `Tom de Smedt <http://organisms.be/>`_, with the purpose of having an equivalent tool in GNU/Linux systems. Nodebox 1 is itself based on `DrawBot <http://www.drawbot.com/>`_ by Just van Rossum. Shoebot draws using the cross-platform `Cairo graphics engine <http://cairographics.org>`_.

It follows a rich lineage of tools dedicated to generative creativity:

  * `Design By Numbers <http://dbn.media.mit.edu/>`_
  * `Processing <http://processing.org>`_
  * `Scriptographer <http://scriptographer.org/>`_
  * `Paper.js <http://paperjs.org/>`_

For more about the nature of creative coding and generative design, be sure to read `The Nodebox 1 theoretical introduction <https://www.nodebox.net/code/index.php/Introduction>`_.

Purpose
-------

Shoebot is a useful tool for many use cases:

* creating generative and procedural works, either for screen or print output
* teaching code to non-developers by means of immediate visual feedback
* prototyping visualizations and design concepts
* automatically generating sets of vector images
* live-coding and real-time tweaking of animated graphics
* making `Cairo <http://cairographics.org>`_-based tools and experiments using a simpler language

Features
--------

Originally built as a GNU/Linux version of Nodebox 1, Shoebot comes with many batteries included:

* supports most of Nodebox 1's functionality
* user-friendly code editor
* headless mode for quick execution without the GUI parts
* run on a window or output files in PDF, PNG, SVG or PS formats
* tweak running scripts via a simple GUI, a socket server or a text-based shell
* can be loaded as a Python module to work inside existing programs


Links
-----

* `Main site <https://shoebot.github.io>`_
* `GitHub repository <https://github.com/shoebot/shoebot>`_
* `Issue tracker <https://github.com/shoebot/shoebot/issues>`_


Authors
-------

Shoebot is currently maintained by `Stuart Axon <https://github.com/stuaxo>`_ and `Ricardo Lafuente <https://github.com/rlafuente>`_.

A good part of the code has also been contributed to by `Francesco Fantoni <https://github.com/hvfrancesco>`_, `Sebastian Oliva <https://github.com/tian2992>`_, `Paulo Silva <https://github.com/nitrofurano>`_, `Dave Crossland <https://github.com/davelab6>`_, `Gabor Papp <https://github.com/gaborpapp>`_, `Julien Deswaef <https://github.com/xuv>`_ , `Pedro Ângelo <https://github.com/pangelo>`_ and Tetsuya Saito. Examples also contributed to by `Artem Popov <https://github.com/artfwo>`_, `Barak Itkin <https://lightningismyname.blogspot.pt/>`_ and `Simon Budig <https://github.com/simon-budig>`_.


Related projects
----------------

* `Drawbot`_, the tool that started it all, by `Just van Rossum <https://twitter.com/justvanrossum>`_ from `Letterror <http://letterror.com>`_. It's now been reinvigorated with new features and experimental Python 3 support.
* `Nodebox 3 <http://nodebox.net/node>`_, the current node-based incarnation of Nodebox, running on Java.
* `Cairo DrawBot <https://github.com/eliheuer/cairo-drawbot>`_, a GNU/Linux compatible fork of Drawbot by `Eli Heuer <https://github.com/eliheuer>`_.
* `Nodebox-pyobjc <https://github.com/karstenw/nodebox-pyobjc>`_, an active fork of Nodebox 1 for Mac, maintained by `Karsten Wolf <https://github.com/karstenw>`_.
* `PlotDevice <https://plotdevice.io/>`_, another fork of Nodebox 1 for Mac, maintained by `Christian Swinehart `http://samizdat.cc/`_.


* `Canvas.js <https://www.clips.uantwerpen.be/pages/pattern-canvas>`_ by Nodebox's co-author `Tom de Smedt`_, allows you to create browser-based scenes and animations with JS and HTML5.
* `Rapydbox <http://salvatore.pythonanywhere.com/RapydBox/default/editor>`_ -- A JavaScript version of Nodebox, based on `RapydScript <https://github.com/atsepkov/RapydScript>`_.



----

Documentation Index
-------------------

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
