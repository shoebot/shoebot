Core
====

  - :ref:`ximport() <ximport()>`
  - :ref:`size() <size()>`
  - :ref:`speed() <speed()>`
  - :ref:`run() <run()>`

.. _ximport():
.. py:function:: ximport(libName)

    Imports a Nodebox library.

    See the :doc:`../libraries` page for a full list.


.. _size():
.. py:function:: size(w, h)

    Sets the size of the canvas. Only
    the first call will have any effect.


.. _speed():
.. py:function:: speed(framerate)

  Sets the frame rate for animations (frames per second), and returns the current
  frame rate.


.. _run():
.. py:function:: run(inputcode, iterations=None, run_forever=False, frame_limiter=False)

  Executes the contents of a Shoebot script in the current surface's context.
