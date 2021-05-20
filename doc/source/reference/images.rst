Images
======

  - :ref:`image() <image()>`
  - :ref:`imagesize() <imagesize()>`

.. _image():
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


.. _imagesize():
.. py:function:: imagesize(path)

    Get the dimensions of an image file as a (width, height) tuple.
