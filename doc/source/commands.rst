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

.. py:function:: rect(x, y, width, height, roundness=0, draw=True)

    Draw a rectangle.

    .. shoebot::
        :alt: four rectangles.  The last three have increasingly round corners.
        :filename: drawing_shapes__rect.png

        fill(0.95, 0.75, 0)
        rect(10, 10, 35, 35)
        # see how roundness affects the shape
        rect(55, 10, 35, 35, 0.3)
        rect(10, 55, 35, 35, 0.7)
        rect(55, 55, 35, 35, 1)


.. py:function:: rectmode(mode=None)

    Change the way rectangles are specified. Each mode alters the parameters
    necessary to draw a rectangle using the :py:func:`rect` function.

    There are 3 different modes available, each expecting different parameters:

    * CORNER mode (default) -- origin point and dimensions (width and height)

      * x-value of the top left corner
      * y-value of the top left corner
      * width
      * height

    * CENTER mode -- draw a shape centered on a point

      * x-coordinate of the rectangle's center point
      * y-coordinate of the rectangle's center point
      * width
      * height

    * CORNERS mode -- origin point and destination point

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

.. py:function:: ellipse(x, y, width, height, draw=True)

    Draw an ellipse by specifying the coordinates of its top left origin point,
    along with its width and height dimensions. See :py:func:`ellipsemode` for
    other ways of drawing ellipses.

    .. shoebot::
        :alt: Two ellipses.
        :filename: drawing_shapes__ellipse.png

        ellipse(10, 20, 30, 60)
        ellipse(50, 30, 40, 40) # circle

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


.. py:function:: line(x1, y1, x2, y2, draw=True)

    Draw a line from (x1,y1) to (x2,y2).

    .. shoebot::
        :alt: 3 crossing lines.
        :filename: drawing_shapes__line.png

        stroke(0.5)
        strokewidth(5)
        line(20, 20, 80, 80)
        line(20, 80, 80, 20)
        line(50, 20, 50, 80)


.. py:function:: arc(x, y, radius, angle1, angle2, type=CHORD, draw=True)

    Draws a circular arc with center at (x,y) between two angles.

    The default arc type (CHORD) only draws the contour of the circle arc
    section. The PIE arc type will close the path connecting the arc points to
    its center, as a pie-chart-like shape.

    .. shoebot::
        :alt: 3 arcs
        :filename: drawing_shapes__arc.png

        nofill()
        stroke(.2)
        autoclosepath(False)
        arc(50, 50, 40, 0, 180)
        arc(50, 50, 30, -90, 0)
        stroke('#ff6633')
        arc(50, 50, 20, 0, 270, type=PIE)


.. py:function:: arrow(x, y, width, type=NORMAL, draw=True)

    Draw an arrow with its tip at (x,y) and the specified width. Its type can be
    NORMAL (default) or FORTYFIVE.

    .. shoebot::
        :alt: An arrow pointing right, and another pointing to the bottom right.
        :filename: drawing_shapes__arrows.png

        arrow(50, 40, 40)
        arrow(90, 40, 40, FORTYFIVE)

.. py:function:: star(x, y, points=20, outer=100, inner=50, draw=True)

    Draw a star-like polygon with its center at (x,y).

    Following the coordinates, this command expects the number of points, the
    outer radius of the star shape, and finally the inner radius.

    .. shoebot::
        :alt: 4 stars.
        :filename: drawing_shapes__stars.png

        star(25, 25, 5, 20, 10)  # top left
        star(75, 25, 10, 20, 3)  # top right
        star(25, 75, 20, 20, 17) # bottom left
        star(75, 75, 40, 20, 19) # bottom right



Bézier paths
------------

.. py:function:: beginpath(x=None, y=None)

    Start a new Bézier path. This command is needed before any other path
    drawing commands such as :py:func:`moveto()`, :py:func:`lineto()`, or
    :py:func:`curveto()`. Finally, the :py:func:`endpath()` command draws the
    path on the screen.

    If x and y are not specified, this command should be followed by a
    :py:func:`moveto` call.

.. py:function:: moveto(x, y)

    Move the Bézier "pen" to the specified point without drawing.

    Can only be called between :py:func:`beginpath()` and :py:func:`endpath()`.

.. py:function:: lineto(x, y)

    Draw a line from the pen's current point to the specified (x,y) coordinates.

    Can only be called between :py:func:`beginpath()` and :py:func:`endpath()`.

.. py:function:: curveto(x1, y1, x2, y2, x3, y3)

    Draws a curve between the current point in the path and a new destination
    point.

    The last two parameters are the coordinates of the destination point. The
    first 4 parameters are the coordinates of the two control points, which
    define the edge and slant of the curve.

    Can only be called between :py:func:`beginpath()` and :py:func:`endpath()`.

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
        strokewidth(12)
        stroke(0.1)

        # Draw the curve
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

.. py:function:: arcto(x, y, radius, angle1, angle2)

    Continues the path with a circular arc in a way identical to :py:func:`arc`.
    A line will be drawn between the current point and the arc's starting point.

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

    Place an image on the canvas with (x,y) as its top left corner. Both bitmap
    and SVG images can be used; in the case of SVG images, the result is
    rendered as paths (not bitmaps).

    If ``width`` and ``height`` are specified, the image is resized to fit.
    The ``alpha`` parameter (0-1) controls the image opacity.

    A filename is expected, but you can use the ``data`` argument instead to
    pass image data as a string or file-like object.

    .. shoebot::
        :alt: Image example
        :filename: image__image.png

        image("source/images/sign.jpg", 0, 0, 100, 100)

.. py:function:: imagesize(path)

    Get the dimensions of an image file as a (width, height) tuple.


Clipping paths
--------------


.. py:function:: beginclip(path)

.. py:function:: endclip()

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



Transforms
----------

.. py:function:: transform(mode=None)

  Sets whether shapes are transformed along their centerpoint or (0,0).

  The mode parameter can be CORNER (default) or CENTER.

  It sets the registration point – the offset for :py:func:`rotate()`,
  :py:func:`scale()` and :py:func:`skew()` commands. By default, primitives,
  text, and images rotate around their own centerpoints. But if you call
  transform() with CORNER as
  its mode parameter, transformations will be applied relative to the canvas
  top left corner (its "origin point") instead.

  See the examples in :py:func:`translate`, :py:func:`rotate`,
  :py:func:`scale` and :py:func:`skew` to see how the transform mode affects
  the result.


.. py:function:: translate(xt, yt)

	Specifies the amount to move the canvas origin point.

  Once called, all commands following translate() are repositioned, which makes
  translate() useful for positioning whole compositions of multiple elements.

  .. shoebot::
      :alt: Two circles
      :filename: transforms__translate.png

      fill(0.2)
      oval(10, 10, 40, 40)
      translate(45, 45)
      oval(10, 10, 40, 40)


.. py:function:: rotate(degrees=0, radians=0)

  Rotates all subsequent drawing commands.

  The default unit is degrees; radians can be used with ``rotate(radians=PI)``.

  This command works incrementally: if you call ``rotate(30)``, and later on
  call ``rotate(60)``, all commands following that second rotate() will be
  rotated 90° (30+60).

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

  This command works incrementally: if you call ``scale(0.5)``, and later on
  call ``scale(0.2)``, all subsequent drawing commands will be sized to 10% (0.2
  of 0.5).

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

  Slants the direction of all subsequent drawing commands.

  The first parameter sets the horizontal skew. The second parameter is optional
  and sets the vertical skew.

  This command works incrementally: if you call ``skew(10)``, and later on call
  ``skew(20)``, all subsequent drawing commands will be skewed by 30° (10+20).

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

  Saves the current transform state.

  The push() function, along with its companion pop(), allows for "saving" a
  transform state. All transformations, such as rotate() and skew(), defined
  between push() and pop() will stop being applied after pop() is called.

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

  Restores the saved transform state.

  This command is meant to be used after push(). It "loads" the transform state
  that was set before the call to push().

.. py:function:: reset()

  Resets the transform state to its default values.

  .. shoebot::
      :alt: Text with transform reset
      :filename: transforms__reset.png

      transform(CENTER)
      rotate(30)
      text("one", 10, 20)
      text("two", 10, 50)
      reset()
      text("three", 10, 80)

Colors
------

  Shapes can be filled, stroked, or both. The :py:func:`fill` and
  :py:func:`stroke` commands are used to set the colors for those operations
  globally. In addition, most drawing commands have ``fill`` and ``stroke``
  parameters to allow setting colors for single objects.

  Fill and stroke colors can be specified in a few ways:

  * grayscale: ``(value)`` and ``(value, alpha)``
  * RGB: ``(red, green, blue)`` and ``(red, green, blue, alpha)``
  * hex colors: ``('#FFFFFF')`` and ``('#FFFFFFFF')``
  * Color objects as created by :py:func:`color`

  The grayscale and RGB options take values between 0 and 1; this behavior can
  be changed with :py:func:`colorrange`.


.. py:function:: background(*args)

  Set the background color.

  .. shoebot::
      :alt: Background example
      :filename: colors__background.png

      background(0.9)
      fill(1)
      circle(40, 40, 20)


.. py:function:: fill(color)

  Sets a fill color, applying it to new paths.

.. py:function:: nofill()

  Stop applying fills to new paths.

  Returns the fill color that was active before the nofill() call.

.. py:function:: stroke(color)

  Set a stroke color, applying it to new paths.

  This command can be used without arguments, in which case it returns the
  current stroke color. When used to set a color, it returns the new color
  value.

.. py:function:: nostroke()

  Stop applying strokes to new paths.

  Returns the stroke color that was active before the nostroke() call.

.. py:function:: strokewidth(w=None)

  Set the width of the stroke in new paths.

  Returns the current stroke width.

.. py:function:: strokedash(dashes, offset=0)

  Sets a dash pattern to be used in stroked shapes.

  A dash pattern is specified by dashes - a list of positive values. Each value
  provides the length of alternate “on” and “off” portions of the stroke.

  The offset specifies an offset into the pattern at which the stroke begins.

  Each “on” segment will have caps applied as if the segment were a separate
  sub-path. In particular, it is valid to use an “on” length of 0 with a round
  or square stroke cap (see :py:func:`strokecap`) in order to distribute dots or
  squares along a path.

  If the number of dashes is 0, dashing is disabled.

  If the number of dashes is 1, a symmetric pattern is assumed with alternating
  on and off portions of the size specified by the single value in dashes.

.. py:function:: strokecap(cap)

  Sets the cap to be drawn at the ends of strokes.

  This command can be called with a new cap value:
  - ``BUTT``: start/stop the line exactly at the start/end point
  - ``ROUND``: use a round ending, the center of the circle is the end point
  - ``SQUARE``: use a squared ending, the center of the square is the end point

  If called with no arguments, returns the current cap value.

.. py:function:: strokejoin(join)

  Sets the join shape to use be drawn at the ends of strokes.

  This command can be called with a new join value:

  - ``MITER``: use a sharp angled corner (default)
  - ``ROUND``: use a rounded join, the center of the circle is the joint point
  - ``BEVEL``: use a cut-off join, the join is cut off at half the line width
    from the joint point

  If called with no arguments, returns the current join value.

.. py:function:: color(*args)

  Returns a Color object that can be stored in a variable and reused.

  .. shoebot::
      :alt: Color reuse
      :filename: color__color.png

      teal = color("#008080")

      rect(20, 20, 60, 15, fill=teal)
      rect(20, 40, 60, 15, fill=teal)
      rect(20, 60, 60, 15)

.. py:function:: colormode(mode=None, crange=None)

  Set the current color mode, which can be RGB or HSB, and optionally
  the color range.


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

.. py:function:: blendmode(mode):

  Sets the blending mode to apply to the colors of new elements.

  Blending modes, also known as Porter-Duff compositing operations, are ways to
  combine two images. Usually, an image (destination) placed on top of another
  (destination) completely covers it; this is the OVER blending mode, but there
  are many others that give distinct results, and which you might know from
  image editors.

  - ``OVER`` -- draw source layer on top of destination layer
  - ``MULTIPLY`` -- source and destination layers are multiplied. This causes the
    result to be at least as dark as the darker inputs.
  - ``SCREEN`` -- source and destination are complemented and multiplied. This
    causes the result to be at least as light as the lighter inputs.
  - ``OVERLAY`` -- multiplies or screens, depending on the lightness of the
    destination color
  - ``DARKEN`` -- replaces the destination with the source if it is darker,
    otherwise keeps the source
  - ``LIGHTEN`` -- replaces the destination with the source if it is lighter,
    otherwise keeps the source.
  - ``COLORDODGE`` -- brightens the destination color to reflect the source color
  - ``COLORBURN`` -- darkens the destination color to reflect the source color
  - ``HARDLIGHT`` -- multiplies or screens, dependent on source color.
  - ``SOFTLIGHT`` -- darkens or lightens, dependent on source color.
  - ``DIFFERENCE`` -- takes the difference of the source and destination color
  - ``EXCLUSION`` -- produces an effect similar to difference, but with lower contrast
  - ``HUE`` -- creates a color with the hue of the source and the saturation and
    luminosity of the target
  - ``SATURATION`` -- creates a color with the saturation of the source and the
    hue and luminosity of the target. Painting with this mode onto a gray area
    produces no change.
  - ``COLOR`` -- creates a color with the hue and saturation of the source and the
    luminosity of the target. This preserves the gray levels of the target and
    is useful for coloring monochrome images or tinting color images.
  - ``LUMINOSITY`` -- creates a color with the luminosity of the source and the
    hue and saturation of the target. This produces an inverse effect to
    COLOR.
  - ``ATOP`` -- draw source on top of destination content and only there
  - ``DEST`` -- ignore the source
  - ``DEST_OVER`` -- draw destination on top of source
  - ``DEST_ATOP`` -- leave destination on top of source content and only there
  - ``XOR`` -- source and destination are shown where there is only one of them
  - ``ADD`` -- source and destination layers are accumulated
  - ``SATURATE`` -- like over, but assuming source and dest are disjoint geometries

  The `Wikipedia page on blending modes
  <https://en.wikipedia.org/wiki/Blend_modes>`_ is a deeper reference on how
  these work, and the `Cairo operators page
  <https://www.cairographics.org/operators/>`_ is also a good resource.

.. py:function:: fillrule(rule=WINDING)

  Sets the fill rule to be used in filled shapes.

  The fill rule is used to determine which regions are inside or outside a
  complex (potentially self-intersecting) path.

Text
----

.. py:function:: text(txt, x, y, width=None, height=None, outline=False, draw=True)

  Draws a string of text according to the current font settings.

  This command takes 3 mandatory arguments: the string of text to write and the
  (x, y) coordinates of the baseline origin.

  If ``width`` is set, the text will wrap (move to the next line) when it exceeds
  the specified value. Setting ``height`` will limit the vertical size of the
  text box, after which no text will be drawn.

  If the ``outline`` option is true, the resulting object will be a BezierPath
  instead of a Text object. It's an alternative to using :py:func:`textpath`.

  .. shoebot::
      :alt: The word 'bot' in bold and italic styles
      :filename: text__text.png

      # when using text(), the origin point
      # is on the text baseline
      arrow(12, 65, 10, type=FORTYFIVE, fill='#ff9966')
      # place the text box
      font("Inconsolata", 50)
      text("Bot", 12, 65)

.. py:function:: font(fontpath=None, fontsize=None)

  Sets the font to be used in new text instances. Accepts a system font name,
  e.g. "Inconsolata Bold", and an optional font size value. Returns the
  current font name.

  A full list of your system's font names can be viewed with the ``pango-list``
  command in a terminal.

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

  Variable fonts are supported. You can specify the value for an axis using
  keyword arguments with the ``var_`` prefix: to set the ``wdth`` axis to
  ``100``, use ``var_wdth=100``.

  Alternatively, you can provide a ``vars`` dictionary with each axis's values,
  e.g. ``font("Inconsolata", vars={"wdth": 100, "wght": 600})``

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

  Sets the size of the current font to use. If called with no parameters,
  returns the current size.

.. py:function:: textpath(txt, x, y, width=None, height=1000000, draw=False)

  Returns an outlined path of the input text.

  For an explanation of the parameters, see :py:func:`text`. Note that, unline
  text(), the ``draw`` option is False by default, as this command is meant
  for doing further manipulation on the text path before rendering it.

.. py:function:: textmetrics(txt, width=None, height=None)

  Returns the width and height of a string of text as a tuple, according to the
  current font settings.

.. py:function:: textwidth(txt, width=None)

  Accepts a string and returns its width, according to the current font
  settings.

.. py:function:: textheight(txt, width=None)

  Accepts a string and returns its height, according to the current font
  settings.

.. py:function:: lineheight(height=None)

  Set the space between lines of text.

.. py:function:: align(align=LEFT)

  Set the way lines of text align with each other. Values can be LEFT, CENTER or RIGHT.

.. py:function:: fontoptions(hintstyle=None, hintmetrics=None, subpixelorder=None, antialias=None)

  Sets text rendering options.

  The ``antialias`` option specifies the type of antialiasing to do:

  - ``default`` -- use the default antialiasing for the subsystem and target device
  - ``none`` -- no antialiasing
  - ``gray`` -- single-color antialiasing
  - ``subpixel`` -- take advantage of the order of subpixel elements on
    devices such as LCD panels
  - ``fast`` -- prefer speed over quality
  - ``good`` -- balance quality against performance
  - ``best`` -- render at the highest quality, sacrificing speed if necessary

  The ``subpixelorder`` sets the order to use with the antialias ``subpixel``
  option:

  - ``rgb`` -- arranged horizontally with red at the left
  - ``bgr`` -- arranged horizontally with blue at the left
  - ``vrgb`` -- arranged vertically with red at the top
  - ``vbgr`` -- arranged vertically with blue at the top

  The ``hintstyle`` option sets the amount of font hinting to apply:

  - ``default`` -- use the default hint style for font backend and target device
  - ``none`` -- do not hint outlines
  - ``slight`` -- improve contrast while retaining good fidelity to the original
    shapes
  - ``medium`` -- compromise between fidelity to the original shapes and
    contrast
  - ``full`` -- maximize contrast

  The ``hintmetrics`` option (``on`` or ``off``) deals with hint metrics, which
  means quantizing (or "rounding") glyph outlines so that they are integer
  values. Doing this improves the consistency of letter and line spacing, but it
  also means that text will be laid out differently at different zoom factors.

Dynamic variables
-----------------

.. py:function:: var(name, type, default=None, min=0, max=255, value=None, step=None, steps=256.0)

  Creates a :doc:`live variable <live>`, which can be manipulated using the
  variables UI, socket server or live coding shell.

  The first two arguments are the variable name and type (NUMBER, TEXT, BOOLEAN
  or BUTTON).

  An optional third argument is the default (initial) value. For NUMBER
  variables, the minimum and maximum values for the variable can be indicated.

  Finally, there are two options for setting the step length on the variables
  interface. This is the "jump" between values if you don't want to use a
  continuous scale. You can either set a fixed number of steps using the
  ``steps`` option, or set a step length with the ``step`` option.

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

  This command returns an iterable object which can be traversed in a loop.

  The first two parameters define the number of columns and rows in the grid.
  The next two parameters are optional, and set the width and height of one cell
  in the grid. In each loop iteration, the offset for the current column and row
  is returned.

  If ``shuffled`` is True, the cells will be returned in a random order.

  .. shoebot::
      :alt: Grid example
      :filename: util__grid.png

      translate(10, 10)
      for x, y in grid(7, 5, 12, 12):
          rect(x, y, 10, 10)

.. py:function:: fontnames()

  Returns a list of system font faces, in the same format that :py:func:`font()`
  expects.

.. py:function:: files(path="*")

  Retrieves all files from a given path and returns their names as a list.
  Wildcards can be used to specify which files to pick, e.g. ``f =
  files('*.gif')``

.. py:function:: autotext(sourceFile)

  Accepts a source file name, and generates mock philosophy based on a
  context-free grammar.


Core
----

.. py:function:: ximport(libName)

    Import a Nodebox library.

    See the :doc:`libraries` page for a full list.

.. py:function:: size(w, h)

    Sets the size of the canvas. Only
    the first call will have any effect.

.. py:function:: speed(framerate)

  Set the frame rate for animations (frames per second), and returns the current
  frame rate.

.. py:function:: run(inputcode, iterations=None, run_forever=False, frame_limiter=False)

  Executes the contents of a Shoebot script in the current surface's context.
