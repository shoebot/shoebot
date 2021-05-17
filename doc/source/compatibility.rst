Nodebox compatibility
=====================

Shoebot was originally developed as a rewrite of Nodebox, attempting to follow its behaviour as close as possible. However, the developers eventually wanted some functionality that was not in Nodebox, and there are many aspects of Nodebox that, for one reason or other, were not ported over.

Now that the original Nodebox isn't being developed further, we have decided to go on and keep implementing original features whenever appropriate.

In this page, you'll find the features and behavior that differs between Nodebox and Shoebot.

If you find any difference that isn't documented here, please `file an issue <https://github.com/shoebot/shoebot/issues/new>`_.

Additional Shoebot features
---------------------------

These are features that were created in Shoebot and are not available in
Nodebox, or where Shoebot behavior is distinct.

New functions
^^^^^^^^^^^^^

- Drawing

  * :py:func:`rectmode()` and :py:func:`ellipsemode()` are inspired by
    Processing and cater to the preferences of users who expect alternative ways
    to draw primitives. These are also useful for specific situations where
    coordinate calculation would be otherwise necessary.
  * :py:func:`arc()` is provided by Cairo, so we support it as well.

- Others

  * :py:func:`snapshot()` is a simple way to output to an image in the middle of
    the script execution.

  * :py:func:`run()` can execute another script in the current context. This is
    mostly useful when using Shoebot as a Python module inside another
    application.

Bundled libraries
^^^^^^^^^^^^^^^^^

Nodebox provides a set of external libraries that can be downloaded and added to
a project. Shoebot comes with ported versions of those libraries already
included and available.

- Knowledge:
  `Database <https://www.nodebox.net/code/index.php/Database>`_,
  `Graph <https://www.nodebox.net/code/index.php/Graph>`_,
  `Web <https://www.nodebox.net/code/index.php/Web>`_

- Bitmap:
  `Photobot <https://www.nodebox.net/code/index.php/Photobot>`_

- Paths:
  `Bezier <https://www.nodebox.net/code/index.php/Bezier>`_,
  `Cornu <https://www.nodebox.net/code/index.php/Cornu>`_,
  `SVG <https://www.nodebox.net/code/index.php/SVG>`_
  `Supershape <https://www.nodebox.net/code/index.php/Supershape>`_,
  `Bezier Editor <https://www.nodebox.net/code/index.php/Bezier_Editor>`_

- Systems:
  `Boids <https://www.nodebox.net/code/index.php/Boids>`_,
  `L-system <https://www.nodebox.net/code/index.php/L-system>`_

- Design:
  `Colors <https://www.nodebox.net/code/index.php/Colors>`_

- Tangible:
  `TUIO <https://www.nodebox.net/code/index.php/TUIO>`_


New libraries
^^^^^^^^^^^^^

Additional external libraries were developed for Shoebot:

* :doc:`libraries/audio`
* :doc:`libraries/video`
* :doc:`libraries/opencv`


Unsupported Nodebox features
----------------------------

These are the Nodebox bits that aren't available in Shoebot.

CMYK color
^^^^^^^^^^

Nodebox was implemented using Mac OS X's Cocoa toolkit, which supports CMYK color. Shoebot runs on the `Cairo <http://cairographics.org>`_ graphics backend, which does not. Nodebox commands that deal with CMYK color are therefore unsupported:

* `outputmode() <https://www.nodebox.net/code/index.php/Reference_|_outputmode()>`_ is not available.
* `colormode() <https://www.nodebox.net/code/index.php/Reference_|_colormode()>`_ is implemented, but ``CMYK`` is not an accepted argument -- only ``RGB`` or ``HSB``.


Path operations
^^^^^^^^^^^^^^^

Operations between bézier paths are not supported yet. These are:

* ``path.union()``
* ``path.intersect()``
* ``path.difference()``

Fitting a path using ``path.fit()`` isn't supported either.

Animation
^^^^^^^^^

While animations work well in a window, Shoebot does not support exporting them to GIF or video formats.

.. _unported-libs:

Unported libraries
^^^^^^^^^^^^^^^^^^

- Knowledge:
  `WordNet <https://www.nodebox.net/code/index.php/WordNet>`_,
  `Keywords <https://www.nodebox.net/code/index.php/Keywords>`_,
  `Linguistics <https://www.nodebox.net/code/index.php/Linguistics>`_

- Bitmap:
  `Core Image <https://www.nodebox.net/code/index.php/Core_Image>`_,
  `iSight <https://www.nodebox.net/code/index.php/iSight>`_,
  `Quicktime <https://www.nodebox.net/code/index.php/Quicktime>`_

- Systems:
  `Ants <https://www.nodebox.net/code/index.php/Ants>`_,
  `Noise <https://www.nodebox.net/code/index.php/Noise>`_

- Design:
  `Grid <https://www.nodebox.net/code/index.php/Grid>`_

- Typography:
  `Pixie <https://www.nodebox.net/code/index.php/Pixie>`_,
  `Fatpath <https://www.nodebox.net/code/index.php/Fatpath>`_

- Tangible:
  `WiiNode <https://www.nodebox.net/code/index.php/WiiNode>`_,
  `OSC <https://www.nodebox.net/code/index.php/OSC>`_

- Other:
  `Flowerewolf <https://github.com/karstenw/Library/tree/master/flowerewolf>`_,
  `twyg <https://github.com/karstenw/Library/tree/master/twyg>`_
