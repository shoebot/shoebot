Text
====

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
