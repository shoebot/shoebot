Command reference
=================

This documentation is still missing many parts. Refer to the [Nodebox
documentation](https://www.nodebox.net/code/index.php/Reference) for the best
reference in the meantime.

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

  * image: Image to draw
  * x: optional, x coordinate (default is image.x)
  * y: optional, y coordinate (default is image.y)


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

Set background to any valid color

.. py:function:: outputmode()

    Not implemented yet (Nodebox API)

.. py:function:: colormode(mode=None, crange=None)

Set the current colormode (can be RGB or HSB) and eventually
the color range.

If called without arguments, it returns the current colormode.

  * mode: Color mode, either "rgb", or "hsb"
  * crange: Maximum scale value for color, e.g. 1.0 or 255

.. py:function:: colorrange(crange)

By default colors range from 0.0 - 1.0 using colorrange
other defaults can be used, e.g. 0.0 - 255.0

  * crange: Color range of 0.0 - 255:

.. py:function:: fill(*args)

Sets a fill color, applying it to new paths.

  * args: color in supported format

.. py:function:: stroke(*args)

Set a stroke color, applying it to new paths.

  * args: color in supported format

.. py:function:: nofill()

Stop applying fills to new paths.

.. py:function:: nostroke()

Stop applying strokes to new paths.

.. py:function:: strokewidth(w=None)

 * w: Stroke width.
 * return: If no width was specified then current width is returned.

.. py:function:: color(*args)

  * args: color in a supported format.
  * return: Color object containing the color.


Color
-----

[TODO: Describe all the possible color syntax options, and link the above
commands to these.]

Text
----

.. py:function:: text(txt, x, y, width=None, height=1000000, outline=False, draw=True)

Draws a string of text according to current font settings.

  * txt: Text to output
  * x: x-coordinate of the top left corner
  * y: y-coordinate of the top left corner
  * width: text width
  * height: text height
  * outline: If True draws outline text (defaults to False)
  * draw: Set to False to inhibit immediate drawing (defaults to True)
  * return: Path object representing the text.


.. py:function:: font(fontpath=None, fontsize=None)

Set the font to be used with new text instances.

Accepts TrueType and OpenType files. Depends on FreeType being
installed.

  * fontpath: path to truetype or opentype font.
  * fontsize: size of font

  * return: current current fontpath (if fontpath param not set)

.. py:function:: fontsize(fontsize=None)

Set or return size of current font.

  * fontsize: Size of font.
  * return: Size of font (if fontsize was not specified)

.. py:function:: textpath(txt, x, y, width=None, height=1000000, draw=False)

Generates an outlined path of the input text.

  * txt: Text to output
  * x: x-coordinate of the top left corner
  * y: y-coordinate of the top left corner
  * width: text width
  * height: text height
  * draw: Set to False to inhibit immediate drawing (defaults to False)
  * return: Path object representing the text.

.. py:function:: textmetrics(txt, width=None, height=None)

  * return: the width and height of a string of text as a tuple (according to current font settings).

.. py:function:: textwidth(txt, width=None)

  * return: the width of a string of text according to the current font settings.

.. py:function:: textheight(txt, width=None)

  * return: the height of a string of text according to the current font settings.

.. py:function:: lineheight(height=None)

Set text lineheight.

  * height: line height.

.. py:function:: align(align="LEFT")

Set text alignment

  * align: Text alignment (LEFT, CENTER, RIGHT)

.. py:function:: fontoptions(hintstyle=None, hintmetrics=None, subpixelorder=None, antialias=None)

    Not implemented yet.

.. py:function:: autotext(sourceFile)

generates mock philosophy based on a context-free grammar


Dynamic variables
-----------------

.. py:function:: var(name, type, default=None, min=0, max=255, value=None)

Utility functions
-----------------

.. py:function:: random(v1=None, v2=None)

.. py:function:: grid(cols, rows, colSize=1, rowSize=1, shuffled=False)

.. py:function:: files(path="*")

    You can use wildcards to specify which files to pick, e.g.
    ``>>> f = files('*.gif')``

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

Set animation framerate.

  * framerate: Frames per second to run bot.
  * return: Current framerate of animation.

.. py:function:: run(inputcode, iterations=None, run_forever=False, frame_limiter=False)

    Executes the contents of a Nodebox or Shoebot script in the current surface's context.
