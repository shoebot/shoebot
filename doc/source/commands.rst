Reference and examples
======================

This is the full list of commands available in Shoebot. This documentation is
still missing some parts. Refer to the `Nodebox documentation
<https://www.nodebox.net/code/index.php/Reference>`_ for the best reference in
the meantime (and where many parts of this documentation are derived from.)

Note that most examples here are drawn on a 100x100 size for simplicity; the
Shoebot default is 300x300px.

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
        strokewidth(15)
        line(20, 20, 80, 80)
        line(20, 80, 80, 20)
        line(50, 20, 50, 80)

.. py:function:: rectmode(mode=None)

    Change the way rectangles are specified. Each mode alters the parameters
    necessary to draw a rectangle using the :py:func:`rect` function.

    * use the CORNER mode (default) when you want to specify an origin point and dimensions (width and height)
    * use the CENTER mode when you want to draw a shape centered on a point
    * use the CORNERS mode when you want to specify an origin point and a destination point

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

    So while you always specify 4 parameters to the :py:func:`rect` function,
    you can use :py:func:`rectmode` to change the function's behaviour according
    to what might suit your script's needs.

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

    Begin drawing a Bézier path.

    After calling beginpath(), a series of other path commands usually follows,
    such as moveto(), lineto(), or curveto(). Finally, the endpath() command
    draws the path on the screen.

    If x and y are not specified, this command should be followed by a
    :py:func:`moveto` call.

    :param x: x-coordinate of the starting point
    :param y: y-coordinate of the starting point
    :type x: float or None
    :type y: float or None

.. py:function:: moveto(x, y)

    Move the Bézier "pen" to the specified point without drawing. Can only be
    called between beginpath() and endpath().

    :param x: x-coordinate of the point to move to
    :param y: y-coordinate of the point to move to
    :type x: float
    :type y: float

.. py:function:: lineto(x, y)

    Draw a line from the pen's current point. Can only be called between
    beginpath() and endpath().

    :param x: x-coordinate of the point to draw to
    :param y: y-coordinate of the point to draw to
    :type x: float
    :type y: float

.. py:function:: curveto(x1, y1, x2, y2, x3, y3)

    Draws a curve between the current point in the path and a new destination
    point. Can only be called between beginpath() and endpath().

    The last two parameters are the coordinates of the destination point. The
    first 4 parameters are the coordinates of the two control points, which
    define the edge and slant of the curve.

    .. shoebot::
        :alt: Curve example
        :filename: path__curveto.png
        :size: 150, 150

        x, y = 10, 62     # Start curve point
        x1, y1 = 50, 115  # Left control point
        x2, y2 = 75, 10   # Right control point
        x3, y3 = 115, 62  # End curve point

        # Only strokes
        autoclosepath(False)
        nofill()

        # Draw the curve
        strokewidth(12)
        stroke(0.1)
        beginpath()
        moveto(x, y)
        curveto(x1, y1, x2, y2, x3, y3)
        endpath()

        # To show where the control points are,
        # we draw helper lines
        strokewidth(2)
        stroke(1, 0.2, 0.2, 0.6)
        # The first control point starts at the
        # x, y position
        line(x, y, x1, y1)
        # And the second control point is the
        # end curve point
        line(x2, y2, x3, y3)

.. py:function:: arc(x, y, radius, angle1, angle2)

.. py:function:: closepath()

 Close the path; in case the current point is not the path's starting point, a
 line will be drawn between them.

.. py:function:: endpath(draw=True)

	The endpath() command is the companion command to beginpath(). When endpath()
	is called, the path defined between beginpath() and endpath() is drawn.
	Optionally, when endpath(draw=False) is called, the path is not drawn but can
	be assigned to a variable and drawn to the screen at a later time with the
	drawpath() command.

.. py:function:: drawpath(path)

  Draws a path on the screen. A path is a series of lines and curves defined
  between beginpath() and endpath(). Normally, endpath() draws the path to the
  screen, unless when calling endpath(draw=False). The path can then be assigned
  to a variable, and this variable used as a parameter for drawpath().

  Note: if you have one path that you want to draw multiple times with
  drawpath(), for example each with its own rotation and position, you need to
  supply a copy: drawpath(path.copy())

    .. shoebot::
        :alt: Drawpath example
        :filename: path__drawpath.png

        stroke(0.2)
        beginpath(10, 10)
        lineto(40, 10)
        p = endpath(draw=False)
        drawpath(p)

.. py:function:: autoclosepath(close=True)

  Defines whether paths are automatically closed by connecting the last and
  first points with a line. It takes a single parameter of True or False. All
  shapes created with beginpath() following this command will adhere to the
  setting.

.. py:function:: findpath(points, curvature=1.0)

  Constructs a fluid path from a list of coordinates. Each element in the list
  is a 2-tuple defining the x-coordinate and the y-coordinate. If the curve has
  more than three points, the curvature parameter offers some control on how
  separate segments are stitched together: from straight lines (0.0) to smooth
  curves (1.0).

    .. shoebot::
        :alt: Findpath example
        :filename: path__findpath.png

        points = [(10, 10), (90, 90), (350, 200)]
        ellipsemode(CENTER)
        for x, y in points:
            ellipse(x, y, 6, 6)

        nofill()
        stroke(0.2)
        autoclosepath(False)
        path = findpath(points)
        drawpath(path)


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
    :type path: filename
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

    The beginclip() and endclip() commands define a clipping mask. The supplied
    parameter defines the path to be used as a clipping mask.

    All basic shapes and path commands return paths that can be used with
    beginclip() - setting the ``draw`` parameter of a shape command will simply
    return the path without actually drawing the shape. Any shapes, paths, texts
    and images between beginclip() and endclip() are `clipped`: any part that
    falls outside the clipping mask path is not drawn.

    .. shoebot::
        :alt: Clipped lines
        :filename: clip__beginclip.png

        p = ellipse(20, 20, 60, 60, draw=False)
        beginclip(p)
        stroke(0.5)
        strokewidth(15)
        line(20, 20, 80, 80)
        line(20, 80, 80, 20)
        line(50, 20, 50, 80)
        endclip()

.. py:function:: endclip()

    Used along with ``beginclip()``.

Transforms
----------

.. py:function:: transform(mode=None)

    The mode parameter sets the registration point – the offset for rotate(),
    scale() and skew() commands. By default, primitives, text, and images rotate
    around their own centerpoints. But if you call transform() with CORNER as
    its mode parameter, transformations will be applied relative to the canvas
    ‘origin point’ rather than being relative to the objects’ centerpoint
    origins.

    Each command example below shows how the transform mode affects the result.

    :param mode: the mode to base new transformations on
    :type mode: CORNER or CENTER

.. py:function:: translate(xt, yt)

	Specifies the amount to move a subsequent shape, path, text, image on the
	screen. Once called, all commands following translate() are repositioned,
	which makes translate() useful for positioning whole compositions of multiple
	elements.

    :param xt: horizontal offset
    :param yt: vertical offset

    .. shoebot::
        :alt: Two circles
        :filename: transforms__translate.png

        fill(0.2)
        oval(-10, -10, 40, 40)
        translate(50, 50)
        oval(-10, -10, 40, 40)

.. py:function:: rotate(degrees=0, radians=0)

  Rotates all subsequent drawing commands. The default unit is degrees; radians
  can be used with ``rotate(radians=PI)``.
  Like other transform operations, the rotate() command works incrementally: if
  you call rotate(30), and later on call rotate(60), all commands following that
  second rotate() will be rotated 90° (30+60).

    :param degrees: angle in degrees
    :param radians: angle in radians

    .. shoebot::
        :alt: Rotated squares
        :filename: transforms__rotate_corner.png

        fill('#4a69bd', 0.2)
        translate(25, 25)
        for i in range(7):
            rotate(15)
            rect(0, 0, 50, 50)

    .. shoebot::
        :alt: Rotated squares
        :filename: transforms__rotate_center.png

        fill('#e55039', 0.2)
        transform(CENTER)
        for i in range(5):
            rotate(15)
            rect(25, 25, 50, 50)


.. py:function:: scale(x=1, y=None)

  Increases, decreases, or streches the size of all subsequent drawing commands.
  The first parameter sets the horizontal scale and the optional second
  parameter the vertical scale. You can also call scale() with a single
  parameter that sets both the horizontal and vertical scale. Scale values are
  specified as floating-point (decimal) numbers with 1.0 corresponding to 100%.

  The scale() command works incrementally: if you call scale(0.5), and later on
  call scale(0.2), all subsequent drawing commands will be sized to 10% (0.2 of
  0.5).

    .. shoebot::
        :alt: Scaled squares
        :filename: transforms__scale_corner.png

        fill('#78e08f', 0.2)
        translate(25,25)
        for i in range(7):
            rect(0, 0, 50, 50)
            scale(.8)

    .. shoebot::
        :alt: Scaled squares
        :filename: transforms__scale_center.png

        fill('#60a3bc', 0.2)
        transform(CENTER)
        for i in range(7):
            rect(25, 25, 50, 50)
            scale(.8)

.. py:function:: skew(x=1, y=0)

  Slants the direction of all subsequent drawing commands. The first parameter
  sets the horizontal skew. The second parameter is optional and sets the
  vertical skew.

  The skew() command works incrementally: if you call skew(10), and later on
  call skew(20), all subsequent drawing commands will be skewed by 30° (10+20).

    .. shoebot::
        :alt: Skewed squares
        :filename: transforms__skew_corner.png

        fill('#82ccdd', 0.2)
        translate(5, 25)
        for i in range(7):
            rect(0, 0, 50, 50)
            skew(.2, 0)

    .. shoebot::
        :alt: Skewed squares
        :filename: transforms__skew_center.png

        fill('#e58e26', 0.2)
        transform(CENTER)
        for i in range(7):
            rect(25, 25, 50, 50)
            skew(.2, 0)

.. py:function:: push()

  The push() function, along with its companion pop(), allows for "saving" a
  transform state. All transformations, such as rotate() and skew(), defined
  between a push() and pop() call last only until pop() is called.

    .. shoebot::
        :alt: Text with push and pop
        :filename: transforms__push_pop.png
        :size: 200, 200

        fill(0.2)
        fontsize(14)
        transform(CENTER)
        rotate(45)
        text("one", 40, 40)

        push()
        rotate(-45)
        text("two", 40, 80)
        pop()

        text("three", 40, 120)


.. py:function:: pop()

  The pop() function is meant to be used after push(). It "loads" the transform
  state that was set before the call to push().

.. py:function:: reset()

  Resets the transform state to its default values.

    .. shoebot::
        :alt: Text with transform reset
        :filename: transforms__reset.png

        rotate(90)
        text("one", 30, 80)
        text("two", 45, 80)

        reset()
        text("three", 70, 80)

Colors
------

  Colors can be specified in a few ways:

    * grayscale: ``(value)``
    * grayscale with alpha: ``(value, alpha)``
    * RGB: ``(red, green, blue)``
    * RGBA: ``(red, green, blue, alpha)``
    * hex: ``('#FFFFFF')``
    * hex with alpha: ``('#FFFFFFFF')``

.. py:function:: background(*args)

  Set the background color.

    .. shoebot::
        :alt: Background example
        :filename: colors__background.png

        background(0.9)
        fill(1)
        circle(40, 40, 20)

.. py:function:: colormode(mode=None, crange=None)

  Set the current color mode (can be RGB or HSB) and eventually
  the color range.

  :param mode: Color mode to use
  :type mode: RGB or HSB
  :param crange: Maximum value for the new color range to use. See `colorrange`_.
  :return: Current color mode (if called without arguments)


.. py:function:: colorrange(crange=1.0)

  Set the numeric range for color values. By default colors range from 0.0 -
  1.0, and this command can set this to a different range. For example,
  a scale of 0 to 255 can be set with ``colorrange(255)``.

    .. shoebot::
        :alt: Color range example
        :filename: colors__colorrange.png

        colorrange(255)
        background(127)
        fill(255)
        circle(40, 40, 20)

.. py:function:: fill(color)

  Sets a fill color, applying it to new paths.

  :param color: color in supported format (see above)

.. py:function:: stroke(color)

  Set a stroke color, applying it to new paths.

  :param color: color in supported format (see above)

.. py:function:: nofill()

  Stop applying fills to new paths.

.. py:function:: nostroke()

  Stop applying strokes to new paths.

.. py:function:: strokewidth(w=None)

  :param w: Stroke width
  :return: Current width (if no width was specified)

.. py:function:: color(*args)

  :param args: color in a supported format
  :return: Color object


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
  :return: BezierPath object representing the text

    .. shoebot::
        :alt: The word 'bot' in bold and italic styles
        :filename: text__text.png

        # when using text(), the origin point
        # is on the text baseline
        ellipsemode(CENTER)
        circle(12, 65, 10, fill='#ff0033')
        # place the text box
        font("Inconsolata", 50)
        text("Bot", 12, 65)

.. py:function:: font(fontpath=None, fontsize=None)

  Set the font to be used in new text instances.

  Accepts a system font name, e.g. "Inconsolata Bold".
  A full list of your system's font names can be viewed with the `pango-list` command in a terminal.

  :param fontpath: font name
  :param fontsize: font size in points
  :return: current font name (if ``fontpath`` was not set)

    .. shoebot::
        :alt: The word 'bot' in bold and italic styles
        :filename: text__font.png

        fill(0.3)
        fontsize(16)

        font("Liberation Mono")
        text("Bot", 35, 25)
        font("Liberation Mono Italic")
        text("Bot", 35, 45)
        font("Liberation Mono Bold")
        text("Bot", 35, 65)
        font("Liberation Mono Bold Italic")
        text("Bot", 35, 85)

  Variable fonts are supported. You can specify the value for an axis using keyword arguments
  with the ``var_`` prefix: to set the ``wdth`` axis to ``100``, use ``var_wdth=100``.

    .. shoebot::
        :alt: The word 'bot' in bold and italic styles
        :filename: text__variablefonts.png

        fill(0.3)
        fontsize(30)

        for x, y in grid(5, 4, 20, 22):
            font("Inconsolata", var_wdth=y+50, var_wght=x*12)
            text("R", 3+x, 25+y)

  Note that for the above example to work, you need to install the variable
  version of `Inconsolata <https://fonts.google.com/specimen/Inconsolata>`_.

.. py:function:: fontsize(fontsize=None)

  Set or return size of current font.

  :param fontsize: Font size in points (pt)
  :return: Font size in points (if ``fontsize`` was not specified)

.. py:function:: textpath(txt, x, y, width=None, height=1000000, draw=False)

  Generates an outlined path of the input text.

  :param txt: Text to output
  :param x: x-coordinate of the top left corner
  :param y: y-coordinate of the top left corner
  :param width: text width
  :param height: text height
  :param draw: Set to False to inhibit immediate drawing (defaults to False)
  :return: Path object representing the text.

.. py:function:: textmetrics(txt, width=None, height=None)

  :return: the width and height of a string of text as a tuple (according to current font settings).

.. py:function:: textwidth(txt, width=None)

  :param text: the text to test for its dimensions
  :return: the width of a string of text according to the current font settings

.. py:function:: textheight(txt, width=None)

  :param text: the text to test for its dimensions
  :return: the height of a string of text according to the current font settings

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

  Returns a random number that can be assigned to a variable or a parameter.
  When no parameters are supplied, returns a floating-point (decimal) number
  between 0.0 and 1.0 (including 0.0 and 1.0). When one parameter is supplied,
  returns a number between 0 and this parameter. When two parameters are
  supplied, returns a number between the first and the second parameter.

    .. shoebot::
        :alt: Random example
        :filename: util__random.png

        r = random() # returns a float between 0 and 1
        r = random(2.5) # returns a float between 0 and 2.5
        r = random(-1.0, 1.0) # returns a float between -1.0 and 1.0
        r = random(5) # returns an int between 0 and 5
        r = random(1, 10) # returns an int between 1 and 10

        # sets the fill to anything from
        # black (0.0,0,0) to red (1.0,0,0)
        fill(random(), 0, 0)
        circle(40, 40, 20)

        # Note: new random values are returned each time the script runs.
        # The variation can be locked by supplying a custom random seed:

        from random import seed
        seed(0)

.. py:function:: grid(cols, rows, colSize=1, rowSize=1, shuffled=False)

  The grid() command returns an iteratable object, something that can be
  traversed in a for-loop (like the range() command for example).

  The grid() is a complex but powerful command. The first two parameters define
  the number of columns and rows in the grid. The next two parameters are
  optional, and set the width and height of one cell in the grid. In each iteration
  of a for-loop, the offset for the current column and row is returned.

    .. shoebot::
        :alt: Grid example
        :filename: util__grid.png

        translate(10, 10)
        for x, y in grid(7, 5, 12, 12):
            rect(x, y, 10, 10)

.. py:function:: fontnames()

    Returns a list of system font faces, in the same format that ``font()``
    expects.

.. py:function:: files(path="*")

    Retrieves all files from a given path and returns their names as a list.
    Wildcards can be used to specify which files to pick, e.g. ``f =
    files('*.gif')``

    :param path: wildcard to use in file list

.. py:function:: autotext(sourceFile)

   Generates mock philosophy based on a context-free grammar.

   :param sourcefile: file path to use as source
   :return: the generated text

.. py:function:: snapshot(filename=None, surface=None, defer=None, autonumber=False)

    Save the contents of current surface into a file or cairo surface/context.

    :param filename: File name to output to. The file type will be deduced from the extension.
    :param surface:  If specified will output snapshot to the supplied cairo surface.
    :param boolean defer: Decides whether the action needs to happen now or can happen later. When set to False, it ensures that a file is written before returning, but can hamper performance. Usually you won't want to do this.  For files defer defaults to True, and for Surfaces to False, this means writing files won't stop execution, while the surface will be ready when snapshot returns. The drawqueue will have to stop and render everything up until this point.
    :param boolean autonumber: If true then a number will be appended to the filename.



Core
----

.. py:function:: ximport(libName)

    Import Nodebox libraries.

    The libraries get access to the _ctx context object, which provides them
    with the Shoebot API.

    :param libName: Library name to import

.. py:function:: size(w=None, h=None)

    Sets the size of the canvas, and creates a Cairo surface and context. Only
    the first call will have any effect.

.. py:function:: speed(framerate)

  Set the framerate for animations.

  :param framerate: Frames per second
  :return: Current framerate

.. py:function:: run(inputcode, iterations=None, run_forever=False, frame_limiter=False)

    Executes the contents of a Shoebot script in the current surface's context.


Classes
-------

.. py:class:: BezierPath

.. py:class:: Text
