Drawing with Shoebot
====================


Primitives
==========

Rectangles
----------

Rectangles can be drawn to the canvas using the rect() function:

    rect(x, y, width, height)

Shoebot also has a rectmode() function, borrowed from Processing and not yet
present in Nodebox, which can be called to change the way rectangles are
specified. Each mode alters the parameters necessary to draw a rectangle using
the rect() function. There are 3 different modes available:

CORNER mode (default)
    * x-value of the top left corner
    * y-value of the top left corner
    * width
    * height

CENTER mode
    * x-coordinate of the rectangle's center point
    * y-coordinate of the rectangle's center point
    * width
    * height

CORNERS mode
    * x-coordinate of the top left corner
    * y-coordinate of the top left corner
    * x-coordinate of the bottom right corner
    * y-coordinate of the bottom right corner

So while you always specify 4 parameters to the rect() function, you can use
rectmode() to change the function's behaviour according to what might suit your
script's needs.

Ellipses and circles
--------------------

Ellipses are available through the ellipse() function:

    ellipse(x, y, width, height)

As you would expect, circles can be achieved by using the same value for the
width and height parameters.

Arrows
------

Spiffy arrows can be drawn with the arrow() function:

    arrow(x, y, size, type)
    
The type parameter can be either NORMAL (the default) or FORTYFIVE. The first draws __,
the second draws a 45 degree arrow (which is quite commonplace in contemporary
graphic design ever since The Designers Republic).

Stars
-----

The star() function can come up with ___

Bézier paths
============

Path commands
-------------

In order to create bézier paths in Shoebot, you need to be acquainted with a few commands: 
  * beginpath
  * moveto
  * lineto
  * curveto
  * arcto (Shoebot and DrawBot only)
  * closepath
  * endpath

Colours: fill and stroke
========================

Colours can be specified in a few ways:
  * grayscale: (value)
  * grayscale with alpha: (value, alpha)
  * RGB: (red, green, blue)
  * RGBA: (red, green, blue, alpha)
  * hex: ('#FFFFFF')
  * hex with alpha: ('#FFFFFFFF')

You can use any of these formats to specify a colour; for example, fill(1,0,0)
and fill('#FF0000') yield the same result.

Fills and strokes can be unset using the nofill() and nostroke() commands,
respectively.

Color ranges
------------

RGB and HSL
-----------

Text
====

Drawing text
------------

Text properties
---------------

Transforms
==========

* explain difference between user-space and device-space
* CENTER and CORNER modes
* translations
* rotating
* scaling
* skewing

Caveat: Shoebot's transform handling code is not optimal; as such, you may
find that executing a script with transforms can be a bit slower, especially
so if you use many transformations at one time. If you need to reduce the
render time in your scripts, your first stop should be cutting on your
transforms.

Rotating
--------

Scaling
-------

Skewing
-------

The transform stack: pushing and popping
----------------------------------------

