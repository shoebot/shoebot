Drawing with Shoebot
====================


Basic shapes
============

.. py:function:: rect(x, y, width, height, roundness=0,0, draw=True, fill=None)

    Draw a rectangle on the canvas.
 
    :param x: x-coordinate of the top left corner
    :param y: y-coordinate of the top left corner
    :param width: rectangle width
    :param height: rectangle height
    :param roundness: rounded corner radius
    :param boolean draw: whether to draw the shape on the canvas or not
    :param fill: fill color


.. py:function:: ellipse(x, y, width, height, draw=True)

    Draw an ellipse on the canvas.
 
    :param x: x-coordinate of the top left corner
    :param y: y-coordinate of the top left corner
    :param width: rectangle width
    :param height: rectangle height
    :param boolean draw: whether to draw the shape on the canvas or not


.. py:function:: arrow(x, y, width, type=NORMAL, draw=True)

    Draw an arrow on the canvas.
 
    :param x: x-coordinate of the top left corner
    :param y: y-coordinate of the top left corner
    :param type: arrow type
    :type type: NORMAL or FORTYFIVE
    :param boolean draw: whether to draw the shape on the canvas or not


.. py:function:: star(startx, starty, points=20, outer=100, inner=50, draw=True)

    Draw a star-like polygon on the canvas.
 
    :param startx: x-coordinate of the top left corner
    :param starty: y-coordinate of the top left corner
    :param points: amount of points
    :param outer: outer radius
    :param inner: inner radius
    :param boolean draw: whether to draw the shape on the canvas or not

    
.. py:function:: rectmode(mode=None)

    Change the way rectangles are specified. Each mode alters the parameters
    necessary to draw a rectangle using the :py:func:`rect` function. 

    :param mode: the mode to draw new rectangles in
    :type mode: CORNER, CENTER or CORNERS

    There are 3 different modes available:

    * CORNER mode (default)
        * x-value of the top left corner
        * y-value of the top left corner
        * width
        * height
    * CENTER mode
        * x-coordinate of the rectangle's center point
        * y-coordinate of the rectangle's center point
        * width
        * height
    * CORNERS mode
        * x-coordinate of the top left corner
        * y-coordinate of the top left corner
        * x-coordinate of the bottom right corner
        * y-coordinate of the bottom right corner

    So while you always specify 4 parameters to the :py:func:`rect` function, you can use
    :py:func:`rectmode` to change the function's behaviour according to what might suit your
    script's needs.


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

Colors: fill and stroke
========================

Colors can be specified in a few ways:
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

