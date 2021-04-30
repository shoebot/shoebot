Colors
======

The Colors library offers a set of tools to work with color more conveniently.

You can use the library to create colors by name (like red or ivory), from
pixels in an image, group them into lists of which you can then collectively
manipulate hue, brightness and saturation, create lists of harmonious colors
based on color theory rules (like complementary or analogous), create lists of
gradient colors, work with drop shadows and gradient fills for paths, define
powerful indefinite color ranges (like bright red or purplishgreenish) and more.

.. contents:: :local:

How to get the library up and running
-------------------------------------

Just place this line at the start of your script:

.. code-block:: python

    colors = ximport("colors")

Outside of Shoebot you can also just ``import colors``. Color lists from image
pixels then work with PIL/Pillow.


(...)

Color list math
---------------

Individual colors (or lists of colors) can be added to a list with the + operator:

.. shoebot::
  :filename: colors__colorlist3.png
  :ximports: colors

  clrs = colors.list(
      colors.purple().darken(),
      colors.deeppink()
  )
  clrs += colors.violet()
  clrs.swarm(50, 50)

Also, the ``*`` operator is equivalent to the ``list.repeat()`` method.
