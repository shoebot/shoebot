Command reference
=================

This documentation is still missing some parts. Refer to the `Nodebox
documentation <https://www.nodebox.net/code/index.php/Reference>`_ for the best
reference in the meantime.

.. contents:: :local:

Drawing shapes
--------------

.. py:function:: rect(x, y, width, height, roundness=0, draw=True, fill=None)

    Draw a rectangle.
 
    :param x: top left x-coordinate
    :param y: top left y-coordinate
    :param width: rectangle width
    :param height: rectangle height
    :param roundness: rounded corner radius
    :param boolean draw: whether to draw the shape on the canvas or not
    :param fill: fill color

    .. shoebot::
        :alt: four rectangles.  The last three have increasingly round corners.
        :filename: drawing_shapes__rect.png

        size(200,200)
        background(1)
        fill(0.95, 0.75, 0)
        rect(10, 10, 35, 35)
        # see how roundness affects the shape
        rect(55, 10, 35, 35, 0.3)
        rect(10, 55, 35, 35, 0.7)
        rect(55, 55, 35, 35, 1)

.. py:function:: ellipse(x, y, width, height, draw=True)

    Draw an ellipse. Same as ``oval()``.
 
    :param x: top left x-coordinate
    :param y: top left y-coordinate
    :param width: ellipse width
    :param height: ellipse height
    :param boolean draw: whether to draw the shape on the canvas or not

    .. shoebot::
        :alt: Two ellipses.
        :filename: drawing_shapes__ellipse.png

        ellipse(10, 20, 30, 60)
        ellipse(50, 30, 40, 40) # circle

.. py:function:: arrow(x, y, width, type=NORMAL, draw=True)

    Draw an arrow.
 
    :param x: arrow tip x-coordinate
    :param y: arrow tip y-coordinate
    :param width: arrow width (also sets height)
    :param type: arrow type
    :type type: NORMAL or FORTYFIVE
    :param boolean draw: whether to draw the shape on the canvas or not

    .. shoebot::
        :alt: An arrow pointing right, and another pointing to the bottom right.
        :filename: drawing_shapes__arrows.png

        arrow(50, 40, 40) # NORMAL is the default arrow type
        arrow(90, 40, 40, FORTYFIVE)

.. py:function:: star(startx, starty, points=20, outer=100, inner=50, draw=True)

    Draw a star-like polygon.
 
    :param startx: center x-coordinate
    :param starty: center y-coordinate
    :param points: amount of points
    :param outer: outer radius
    :param inner: inner radius
    :param boolean draw: whether to draw the shape on the canvas or not

    .. shoebot::
        :alt: 4 stars.
        :filename: drawing_shapes__stars.png

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
        :alt: 3 crossing lines.
        :filename: drawing_shapes__line.png

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

    .. shoebot::
        :alt: green rectangle top left, blue centered and red at the bottom right.
        :filename: drawing_shapes__rectmode.png

        nofill()
        strokewidth(2)

        rectmode(CORNER)  # default, red
        stroke(0.8, 0.1, 0.1)
        rect(25, 25, 40, 40)

        rectmode(CENTER)  # green
        stroke(0.1, 0.8, 0.1)
        rect(25, 25, 40, 40)

        rectmode(CORNERS)  # blue
        stroke(0.1, 0.1, 0.8)
        rect(25, 25, 40, 40)

.. py:function:: ellipsemode(mode=None)

    Change the way ellipses are specified. Each mode alters the parameters
    necessary to draw an ellipse using the :py:func:`ellipse` function. 

    It works exactly the same as the :py:func:`rectmode` command.

    .. shoebot::
        :alt: green ellipse top left, blue centered and red at the bottom right.
        :filename: drawing_shapes__ellipsemode.png

        nofill()
        strokewidth(2)

        ellipsemode(CORNER)  # default, red
        stroke(0.8, 0.1, 0.1)
        ellipse(25, 25, 40, 40)

        ellipsemode(CENTER)  # green
        stroke(0.1, 0.8, 0.1)
        ellipse(25, 25, 40, 40)

        ellipsemode(CORNERS)  # blue
        stroke(0.1, 0.1, 0.8)
        ellipse(25, 25, 40, 40)

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

    Move the Bézier "pen" to the specified point without drawing; coordinates are absolute.

    :param x: x-coordinate of the point to move to
    :param y: y-coordinate of the point to move to
    :type x: float
    :type y: float

.. py:function:: relmoveto(x, y)

    Move the Bézier "pen" to the specified point without drawing; coordinates are relative to the pen's current location.

    :param x: x-coordinate of the point to move to, relative to the pen's current point
    :param y: y-coordinate of the point to move to, relative to the pen's current point
    :type x: float
    :type y: float

.. py:function:: lineto(x, y)

    Draw a line from the pen's current point; coordinates are absolute.

    :param x: x-coordinate of the point to draw to, relative to the pen's current point
    :param y: y-coordinate of the point to draw to, relative to the pen's current point
    :type x: float
    :type y: float

.. py:function:: rellineto(x, y)

    Draw a line from the pen's current point; coordinates are relative to the pen's current location.

    :param x: x-coordinate of the point to draw to, relative to the pen's current point
    :param y: y-coordinate of the point to draw to, relative to the pen's current point
    :type x: float
    :type y: float

.. py:function:: curveto(x1, y1, x2, y2, x3, y3)

.. py:function:: arc(x, y, radius, angle1, angle2)

.. py:function:: closepath()

   Close the path; in case the current point is not the path's starting point, a line will be drawn between them.

.. py:function:: endpath(draw=True)

.. py:function:: drawpath(path)

.. py:function:: autoclosepath(close=True)

.. py:function:: findpath(points, curvature=1.0)


Images
------

.. py:function:: image(path, x=0, y=0, width=None, height=None, alpha=1.0, data=None, draw=True)

    Place a bitmap image on the canvas.

    :param path: location of the image on disk
    :param x: x-coordinate of the top left corner
    :param y: y-coordinate of the top left corner
    :param width: image width (leave blank to use its original width)
    :param height: image height (leave blank to use its original height)
    :param alpha: opacity
    :param data: image data to load. Use this instead of ``path`` if you want to load an image from memory or have another source (e.g. using the `web` library)
    :param draw: whether to place the image immediately on the canvas or not
    :type path: str
    :type x: float
    :type y: float
    :type width: float or None
    :type height: float or None
    :type alpha: float
    :type data: binary data
    :type draw: bool


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
  * grayscale: ``(value)``
  * grayscale with alpha: ``(value, alpha)``
  * RGB: ``(red, green, blue)``
  * RGBA: ``(red, green, blue, alpha)``
  * hex: ``('#FFFFFF')``
  * hex with alpha: ``('#FFFFFFFF')``

You can use any of these formats to specify a colour; for example, `fill(1,0,0)`
and `fill('#FF0000')` yield the same result.

.. py:function:: background(*args)

Set background to any valid color

.. py:function:: outputmode()

    Not implemented yet (Nodebox API)

.. py:function:: colormode(mode=None, crange=None)

  Set the current colormode (can be RGB or HSB) and eventually
  the color range.

  :param mode: Color mode to use
  :type mode: RGB or HSB
  :param crange: Maximum value for the new color range to use. See `colorrange`_.
  :rtype: Current color mode (if called without arguments)


.. py:function:: colorrange(crange=1.0)

  Set the numeric range for color values. By default colors range from 0.0 - 1.0; use this to set a different range, e.g. with ``colorrange(255)`` values will range between 0 and 255.

  :param crange: Maximum value for the new color range to use
  :type crange: float


.. py:function:: fill(*args)

  Sets a fill color, applying it to new paths.

  :param args: color in supported format

.. py:function:: stroke(*args)

  Set a stroke color, applying it to new paths.

  :param args: color in supported format

.. py:function:: nofill()

  Stop applying fills to new paths.

.. py:function:: nostroke()

  Stop applying strokes to new paths.

.. py:function:: strokewidth(w=None)

  :param w: Stroke width
  :rtype: Current width (if no width was specified)

.. py:function:: color(*args)

  :param args: color in a supported format
  :rtype: Color object


Text
----

.. py:function:: text(txt, x, y, width=None, height=1000000, outline=False, draw=True)

  Draws a string of text according to current font settings.

  :param txt: Text to output
  :param x: x-coordinate of the top left corner
  :param y: y-coordinate of the top left corner
  :param width: text box width. When set, text will wrap to the next line if it would exceed this width. If unset, there will be no line breaks.
  :param height: text box height
  :param outline: whether to draw as an outline.
  :param draw: if False, the object won't be immediately drawn to canvas.
  :type outline: bool
  :type draw: bool
  :rtype: BezierPath object representing the text


.. py:function:: font(fontpath=None, fontsize=None)

  Set the font to be used with new text instances.

  Accepts a system font name, e.g. "Inconsolata".

  :param fontpath: font name
  :param fontsize: font size in points
  :rtype: current font path (if ``fontpath`` was not set)

.. py:function:: fontsize(fontsize=None)

  Set or return size of current font.

  :param fontsize: Font size in points (pt)
  :rtype: Font size in points (if ``fontsize`` was not specified)

.. py:function:: textpath(txt, x, y, width=None, height=1000000, draw=False)

  Generates an outlined path of the input text.

  :param txt: Text to output
  :param x: x-coordinate of the top left corner
  :param y: y-coordinate of the top left corner
  :param width: text width
  :param height: text height
  :param draw: Set to False to inhibit immediate drawing (defaults to False)
  :rtype: Path object representing the text.

.. py:function:: textmetrics(txt, width=None, height=None)

  :rtype: the width and height of a string of text as a tuple (according to current font settings).

.. py:function:: textwidth(txt, width=None)

  :param text: the text to test for its dimensions
  :rtype: the width of a string of text according to the current font settings

.. py:function:: textheight(txt, width=None)

  :param text: the text to test for its dimensions
  :rtype: the height of a string of text according to the current font settings

.. py:function:: lineheight(height=None)

  Set the space between lines of text.

  :param height: line height

.. py:function:: align(align=LEFT)

  Set the way lines of text align with each other.

  :param align: Text alignment rule
  :type align: LEFT, CENTER or RIGHT

.. py:function:: fontoptions(hintstyle=None, hintmetrics=None, subpixelorder=None, antialias=None)

    Not implemented.

Dynamic variables
-----------------

.. py:function:: var(name, type, default=None, min=0, max=255, value=None, step=None, steps=256.0)

  Create a :doc:`live variable <live>`.

  :param name: Variable name
  :param type: Variable type
  :type type: NUMBER, TEXT, BOOLEAN or BUTTON
  :param default: Default value
  :param min: Minimum value (NUMBER only)
  :param max: Maximum value (NUMBER only)
  :param value: Initial value (if not defined, use ``default``)
  :param step: Step length for the variables GUI (use this or ``steps``, not both)
  :param steps: Number of steps in the variables GUI (use this or ``step``, not both)

Utility functions
-----------------

.. py:function:: random(v1=None, v2=None)

.. py:function:: grid(cols, rows, colSize=1, rowSize=1, shuffled=False)

.. py:function:: files(path="*")

    You can use wildcards to specify which files to pick, e.g. ``f = files('*.gif')``

    :param path: wildcard to use in file list

.. py:function:: autotext(sourceFile)

   Generates mock philosophy based on a context-free grammar.

   :param sourcefile: file path to use as source
   :rtype: the generated text

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

  Set the framerate on windowed mode.

  :param framerate: Frames per second
  :rtype: Current framerate

.. py:function:: run(inputcode, iterations=None, run_forever=False, frame_limiter=False)

    Executes the contents of a Nodebox or Shoebot script in the current surface's context.
