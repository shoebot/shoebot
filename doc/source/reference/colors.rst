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

  .. shoebot::
    :alt: Stroke widths
    :filename: color__strokewidth.png

    stroke(0.2)
    strokewidth(1)
    line(20, 20, 20, 110)
    strokewidth(3)
    line(40, 20, 40, 110)
    strokewidth(10)
    line(60, 20, 60, 110)
    strokewidth(15)
    line(80, 20, 80, 110)


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

  .. shoebot::
    :alt: Stroke dashes
    :filename: color__strokedash.png

    nofill()
    stroke(0.2)
    strokewidth(3)

    circle(5,5,40)

    strokedash([3,2,1,2])
    circle(55,5,40)

    strokedash([10,15,5])
    circle(5,55,40)

    strokedash([10,15,5], 20)
    strokecap(ROUND)
    circle(55,55,40)


.. py:function:: strokecap(cap)

  Sets the cap to be drawn at the ends of strokes.

  This command can be called with a new cap value:

  - ``BUTT`` -- start/stop the line exactly at the start/end point
  - ``ROUND`` -- use a round ending, the center of the circle is the end point
  - ``SQUARE`` -- use a squared ending, the center of the square is the end point

  If called with no arguments, returns the current cap value.

  .. shoebot::
    :alt: Stroke caps
    :filename: color__strokecap.png

    stroke(0.2)
    strokewidth(15)
    line(25, 25, 25, 110)
    strokecap(ROUND)
    line(50, 25, 50, 110)
    strokecap(SQUARE)
    line(75, 25, 75, 110)


.. py:function:: strokejoin(join)

  Sets the join shape to use be drawn at the ends of strokes.

  This command can be called with a new join value:

  - ``MITER`` -- use a sharp angled corner (default)
  - ``ROUND`` -- use a rounded join, the center of the circle is the joint point
  - ``BEVEL`` -- use a cut-off join, the join is cut off at half the line width
    from the joint point

  If called with no arguments, returns the current join value.

  .. shoebot::
    :alt: Stroke joins
    :filename: color__strokejoin.png

    autoclosepath(False)
    nofill()
    stroke(0.2)
    strokewidth(15)

    beginpath(10,25)
    lineto(40,50)
    lineto(10,75)
    endpath()
    translate(25,0)

    strokejoin(ROUND)
    beginpath(10,25)
    lineto(40,50)
    lineto(10,75)
    endpath()
    translate(25,0)

    strokejoin(BEVEL)
    beginpath(10,25)
    lineto(40,50)
    lineto(10,75)
    endpath()


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
  - ``HARDLIGHT`` -- multiplies or screens, dependent on source color
  - ``SOFTLIGHT`` -- darkens or lightens, dependent on source color
  - ``DIFFERENCE`` -- takes the difference of the source and destination color
  - ``EXCLUSION`` -- produces an effect similar to difference, but with lower
    contrast
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
