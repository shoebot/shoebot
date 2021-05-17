Core
====

.. py:function:: ximport(libName)

    Import a Nodebox library.

    See the :doc:`../libraries` page for a full list.

.. py:function:: size(w, h)

    Sets the size of the canvas. Only
    the first call will have any effect.

.. py:function:: speed(framerate)

  Set the frame rate for animations (frames per second), and returns the current
  frame rate.

.. py:function:: run(inputcode, iterations=None, run_forever=False, frame_limiter=False)

  Executes the contents of a Shoebot script in the current surface's context.
