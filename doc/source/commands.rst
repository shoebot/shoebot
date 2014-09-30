Command reference
=================

Drawing shapes
--------------

.. py:function:: rect(x, y, width, height, roundness=0, draw=True, fill=None)

    Draw a rectangle on the canvas.
 
    :param x: top left x-coordinate
    :param y: top left y-coordinate
    :param width: rectangle width
    :param height: rectangle height
    :param roundness: rounded corner radius
    :param boolean draw: whether to draw the shape on the canvas or not
    :param fill: fill color

    .. shoebot::
        :snapshot:

        rect(10, 10, 35, 35)
        # see how roundness affects the shape
        rect(55, 10, 35, 35, 0.3)
        rect(10, 55, 35, 35, 0.7)
        rect(55, 55, 35, 35, 1)

.. py:function:: ellipse(x, y, width, height, draw=True)

    Draw an ellipse on the canvas. Same as `oval()`.
 
    :param x: top left x-coordinate
    :param y: top left y-coordinate
    :param width: ellipse width
    :param height: ellipse height
    :param boolean draw: whether to draw the shape on the canvas or not

    .. shoebot::
        :snapshot:

        ellipse(10, 20, 30, 60)
        ellipse(50, 30, 40, 40) # circle

.. py:function:: arrow(x, y, width, type=NORMAL, draw=True)

    Draw an arrow on the canvas.
 
    :param x: arrow tip x-coordinate
    :param y: arrow tip y-coordinate
    :param width: arrow width (also sets height)
    :param type: arrow type
    :type type: NORMAL or FORTYFIVE
    :param boolean draw: whether to draw the shape on the canvas or not

    .. shoebot::
        :snapshot:

        arrow(50, 40, 40) # NORMAL is the default arrow type
        arrow(90, 40, 40, FORTYFIVE)

.. py:function:: star(startx, starty, points=20, outer=100, inner=50, draw=True)

    Draw a star-like polygon on the canvas.
 
    :param startx: center x-coordinate
    :param starty: center y-coordinate
    :param points: amount of points
    :param outer: outer radius
    :param inner: inner radius
    :param boolean draw: whether to draw the shape on the canvas or not

    .. shoebot::
        :snapshot:

        star(25, 25, 5, 20, 10)  # top left
        star(75, 25, 10, 20, 3)  # top right
        star(25, 75, 20, 20, 17) # bottom left
        star(75, 75, 40, 20, 19) # bottom right

.. py:function:: line(x1, y1, x2, y2, draw=True)

    Draw a line from (x1,y1) to (x2,y2).
    
    :param x1: x-coordinate of the first point
    :param y1: y-coordinate of the first point
    :param x2: x-coordinate of the second point
    :param y2: y-coordinate of the second point
    :param boolean draw: whether to draw the shape on the canvas or not
    
    .. shoebot::
        :snapshot:

        stroke(0.5)
        strokewidth(3)
        line(20, 20, 80, 80)
        line(20, 80, 80, 20)
        line(50, 20, 50, 80)

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
------------

.. py:function:: beginpath(x=None, y=None)

    Begin drawing a Bézier path. If x and y are not specified, this command
    should be followed by a :py:func:`moveto` call.

    :param x: x-coordinate of the starting point
    :param y: y-coordinate of the starting point
    :type x: float or None
    :type y: float or None

.. py:function:: moveto(x, y)

.. py:function:: relmoveto(x, y)

.. py:function:: lineto(x, y)

.. py:function:: rellineto(x, y)

.. py:function:: curveto(x1, y1, x2, y2, x3, y3)

.. py:function:: arc(x, y, radius, angle1, angle2)

.. py:function:: closepath()

.. py:function:: endpath(draw=True)

.. py:function:: drawpath(path)

.. py:function:: autoclosepath(close=True)

.. py:function:: findpath(points, curvature=1.0)


Images
------

.. py:function:: drawimage(image)

Clipping paths
--------------

.. py:function:: beginclip(path)

.. py:function:: endclip()


Transforms
----------

.. py:function:: transform(mode=None)

    :param mode: the mode to base new transformations on
    :type mode: CORNER or CENTER

.. py:function:: translate(xt, yt, mode=None)

.. py:function:: rotate(degrees=0, radians=0)

.. py:function:: scale(x=1, y=None)

.. py:function:: skew(x=1, y=0)

.. py:function:: push()

.. py:function:: pop()

.. py:function:: reset()


Colors
------

Colors can be specified in a few ways:
  * grayscale: `(value)`
  * grayscale with alpha: `(value, alpha)`
  * RGB: `(red, green, blue)`
  * RGBA: `(red, green, blue, alpha)`
  * hex: `('#FFFFFF')`
  * hex with alpha: `('#FFFFFFFF')`

You can use any of these formats to specify a colour; for example, `fill(1,0,0)`
and `fill('#FF0000')` yield the same result.

.. py:function:: background(*args)

.. py:function:: outputmode()

.. py:function:: colormode(mode=None, crange=None)

.. py:function:: colorrange(crange)

.. py:function:: fill(*args)

.. py:function:: stroke(*args)

.. py:function:: nofill()

.. py:function:: nostroke()

.. py:function:: strokewidth(w=None)

.. py:function:: color(*args)


Text
----

.. py:function:: text(txt, x, y, width=None, height=1000000, outline=False, draw=True)

.. py:function:: font(fontpath=None, fontsize=None)

.. py:function:: fontsize(fontsize=None)

.. py:function:: textpath(txt, x, y, width=None, height=1000000, draw=False)

.. py:function:: textmetrics(txt, width=None, height=None)

.. py:function:: textwidth(txt, width=None)

.. py:function:: textheight(txt, width=None)

.. py:function:: lineheight(height=None)

.. py:function:: align(align="LEFT")

.. py:function:: fontoptions(hintstyle=None, hintmetrics=None, subpixelorder=None, antialias=None)

    Not implemented yet.

.. py:function:: autotext(sourceFile)


Dynamic variables
-----------------

.. py:function:: var(name, type, default=None, min=0, max=255, value=None)

Utility functions
-----------------

.. py:function:: random(v1=None, v2=None)

.. py:function:: grid(cols, rows, colSize=1, rowSize=1, shuffled=False)

.. py:function:: files(path="*")

    You can use wildcards to specify which files to pick, e.g.
    >>> f = files('*.gif')

    :param path: wildcard to use in file list.


.. py:function:: snapshot(filename=None, surface=None, defer=None, autonumber=False)

    Save the contents of current surface into a file or cairo surface/context.

    :param filename: File name to output to. The file type will be deduced from the extension.
    :param surface:  If specified will output snapshot to the supplied cairo surface.
    :param boolean defer: Decides whether the action needs to happen now or can happen later. When set to False, it ensures that a file is written before returning, but can hamper performance. Usually you won't want to do this.  For files defer defaults to True, and for Surfaces to False, this means writing files won't stop execution, while the surface will be ready when snapshot returns. The drawqueue will have to stop and render everything up until this point.
    :param boolean autonumber: If true then a number will be appended to the filename.



Core
----

.. py:function:: ximport(libName)

    Import nodebox libraries.

    The libraries get _ctx, which provides
    them with the nodebox API.

    :param libName: Library name to import

.. py:function:: size(w=None, h=None)

    Sets the size of the canvas, and creates a Cairo surface and context. Only the first call will actually be effective.

.. py:function:: speed(framerate)

.. py:function:: run(inputcode, iterations=None, run_forever=False, frame_limiter=False)

    Executes the contents of a Nodebox or Shoebot script in the current surface's context.
