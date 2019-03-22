Libraries
=========

Nodebox libraries
-----------------

Nodebox has a rich set of external libraries to enable new tools and commands.

Shoebot comes with some of these external libraries included. Read the original Nodebox documentation to get these going:

- Knowledge: 
  `Database <https://www.nodebox.net/code/index.php/Database>`_,
  `Graph <https://www.nodebox.net/code/index.php/Graph>`_, 
  `Web <https://www.nodebox.net/code/index.php/Web>`_

- Bitmap:  
  `Photobot <https://www.nodebox.net/code/index.php/Photobot>`_

- Paths: 
  `Bezier <https://www.nodebox.net/code/index.php/Bezier>`_,
  `Cornu <https://www.nodebox.net/code/index.php/Cornu>`_, 
  `SVG <https://www.nodebox.net/code/index.php/SVG>`_
  `Supershape <https://www.nodebox.net/code/index.php/Supershape>`_, 
  `Bezier Editor <https://www.nodebox.net/code/index.php/Bezier_Editor>`_

- Systems: 
  `Boids <https://www.nodebox.net/code/index.php/Boids>`_, 
  `L-system <https://www.nodebox.net/code/index.php/L-system>`_

- Design:
  `Colors <https://www.nodebox.net/code/index.php/Colors>`_

- Tangible: 
  `TUIO <https://www.nodebox.net/code/index.php/TUIO>`_



Shoebot libraries
-----------------

Shoebot also includes a set of libraries of its own. We still have to document them. Ping us on the `issue tracker <https://github.com/shoebot/shoebot/issues>`_ if you need help.

.. _audio-lib:

Audio
^^^^^

Grab audio frequencies to create visualizations.

Import it with ``ximport("sbaudio")``.

Requires the ``pysoundcard`` Python module to work. 

.. py:function:: fft_bandpassfilter(data, fs, lowcut, highcut)

.. py:function:: flatten_fft(scale=1.0)

.. py:function:: scaled_fft(fft, scale=1.0)

.. py:function:: triple(spectrogram)

.. py:function:: fuzzydevices(match="", min_ratio=30)

.. py:function:: firstfuzzydevice(match="")

.. _video-lib:

Video
^^^^^

This is a **very** basic video library. The library itself is built upon OpenCV, a library of programming functions mainly aimed at real time computer vision.

You need ``opencv`` and its python bindings in order to use this library, so on debian-based Linux you will
have to install ``python-opencv`` and ``libhighgui1`` or similar.

The Video Library is meant to grab frames from webcams, surveillance cameras or video files, and to make them available to Shoebot for displaying and elaboration.

For cameras, two camera interfaces can be used on Windows: Video for Windows (VFW) and Matrox Imaging Library (MIL). On Linux, we can use V4L and FireWire (IEEE1394).

For video files, this library uses specific backends on each OS:

  * ffmpeg on Linux
  * Video for Windoes (VfW) on Windows
  * QuickTime on Mac OS X

Up to now only camera and video frame grabbing is supported, but future development could introduce features like face and object recognition or video output to file for Shoebot animation. Future development will depend on evolution of the SWIG python bindings of OpenCV, which at present is still in-progress.

Basic usage
+++++++++++

First, import the library:

.. code-block:: python

    videolib = ximport("sbvideo")

Then you can create two different types of capture devices:

.. code-block:: python

    # for video files 
    video = videolib.movie(file_path)
    # or for webcam 
    camera = videolib.camera(index, width, height) 

If you have only one camera, you can omit ``index`` and the first camera should be picked. Parameters ``width`` and ``height`` are optional, and they're not guaranteed to work with your camera. Now you can grab a video frame with:

.. code-block:: python

    frame = video.frame() or frame = camera.frame()

frame has some properties:
frame.width
frame.height
frame.time  # strange results at present
frame.data

You need ``frame.data`` in order to pass your frame image to the Shoebot canvas using the :py:func:`image()` command:

.. code-block:: python

    image(None, xpos, ypos, data=frame.data)

You can manipulate and use the image as any other image in Shoebot.

When you call the video-file capture constructor, you're supposed to be able to set a starting point in seconds from
file beginning, but at present this feature is disabled as I could not get it to work properly on my linux system
If you want to test it you can uncomment the relative lines in SVL. (If you succeed, please report it to Shoebot dev mailing list).

Commands
++++++++

.. py:function:: sbvideo.movie(path, start=0, stop=None)

.. py:function:: sbvideo.camera(cam=0, width=None, height=None)

.. _opencv-lib:

OpenCV
^^^^^^

.. py:function:: sbopencv.movie(path, start=0, stop=None)

.. py:function:: sbopencv.camera(cam=0, width=None, height=None)

.. py:function:: sbopencv.image(path=None)

.. py:function:: sbopencv.ipl2cairo(iplimage)

.. py:function:: sbopencv.detectHaar(iplimage, classifier)

.. py:function:: sbopencv.findcontours(iplimage, threshold=100)
