Colors
======

The Colors library offers a set of tools to work with color more conveniently.

You should read the original Nodebox documentation for the `Colors
library <https://www.nodebox.net/code/index.php/Boids>`_. The below parts
are a work in progress port of the Nodebox docs.

----

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

Colors
------

The Colors library has a number of commands that create a new color you can use
with fill() or stroke().

.. code-block:: python

    rgb(r, g, b, a=None, range=1.0, name="")
    hsb(h, s, b, a=None, range=1.0, name="")
    cmyk(c, m, y, k, range=1.0, name="")
    lab(l, a, b, range=1.0, name="")
    hex(str, name="")

With the range parameter you can define how you want to supply the channel
values. For example, if you want to define r, g and b between 0 and 255 instead
of between 0.0 and 1.0, set range to 255.

The optional name parameter lets you define a name for the color. Otherwise, a
name will be guessed using the clr.nearest_hue() method (see below).

The hex() command creates a color from a hexadecimal string (e.g. "#30343D").

The named_color() command creates a color from a name like "olive" or "maroon"
or "antiquewhite". A list of all the named colors the command will recognize is
here. The really great thing is that each of these named colors is also a
command in the Colors library. So the two colors in the example below are
exactly the same:

.. code-block:: python

  clr1 = colors.named_color("olive")
  clr2 = colors.olive()

Color properties
----------------

Each of the above commands returns a Color object. It has all the standard
properties a color created with the NodeBox color() command also has. You can
use these to find out the color's R, B and B values, or its C, M, Y and K
values, or its H, S and B values:

- clr.r: the red value in RGB.
- clr.g: the green value in RGB.
- clr.b: the blue value in RGB.
- clr.a: the alpha value (opacity).
- clr.c: the cyan value in CMYK.
- clr.m: the magenta value in CMYK.
- clr.y: the yellow value in CMYK.
- clr.k: the black value in CMYK.
- clr.hue: the hue of the color in HSB.
- clr.saturation: the saturation (grayness) of the color in HSB.
- clr.brightness: the brightness of the color in HSB.

The Color object in the Colors Library has some additional properties:

- clr.name: the name of this color.
- clr.is_black: will be True when the color's R, G and B values are 0.
- clr.is_white: will be True when the color's R, G and B values are 1.
- clr.is_gray: will be True when the color's R, G and B values are the same.
- clr.is_transparent: will be True when the color is completely transparent.
- clr.complement: the complementary color (i.e. 180 degrees across the color wheel) of this color.



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
