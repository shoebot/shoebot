Shoebot Video Library v0.0.1

i've put togheter a VERY basic video library for Shoebot (http://tinkerhouse.net/shoebot)
The library itself is built upon opencv, OpenCV (Open Source Computer Vision) is a library of
programming functions mainly aimed at real time computer vision.
You need opencv and its python bindings in order to use this library, so on debian-based Linux you will
have to install python-opencv and libhighgui1 packages or similar packages providing the right dependencies.

OpenCV is a multi-platform library, but I have no idea about how to install it in windows, please refer to
OpenCV wiki site (http://opencv.willowgarage.com/wiki/Welcome) for help and informations.

The Shoebot Video Library (SVL from now on) is meant to grab frames from web-camera, surveillance cameras or video-files,
and to make them available to shoebot for displaying and elaboration.

For cameras, two camera interfaces can be used on Windows: Video for Windows (VFW) and Matrox Imaging Library (MIL)
and two on Linux: V4L and FireWire (IEEE1394).
For video files SVL uses on windows Video for Windows (VfW), on Linux it uses ffmpeg, while on Mac OS X it could use QuickTime as backend. The codecs supported by the used backend should work, but it's not sure, you should test it.

Up to now only camera and video frame grabbing is supported, but future development could introduce features like face and object recognition or video output to file for shoebot animation.
Actually the future development will depend on evolution of SWIG python bindings of OpenCV, that at present is still in-progress.

Basic usage:
first of all you have to place SVL folder in /usr/share/shoebot/lib (or symlink it) and then import the SVL with following syntax:

videolib = ximport("sbvideo")

then you can create two different types of capture devices:
e.g. for video files - video = videolib.movie(file_path)
for webcam - camera = videolib.camera(index, width, height) 
if you have only one camera you can omit index and first camera should be picked, otherwise you can indicate camera index.
width and height parameters are optional, and anyway I cannot guarantee they actually work with your camera.

then you can grab a video frame with:

frame = video.frame() or frame = camera.frame()

frame has some properties:
frame.width
frame.height
frame.time (strange results at present)
frame.data

frame.data is the thing you need in order to pass your frame image to shoebot canvas using image() command:

image(None, xpos, ypos, data=frame.data)

Of course you can manipulate and use the image as any other image in Shoebot.

When you call the video-file capture constructor, you're supposed to be able to set a starting point in seconds from
file beginning, but at present this feature is disabled as I could not get it to work properly on my linux system
If you want to test it you can uncomment the relative lines in SVL. (If you succeed, please report it to Shoebot dev mailing list).

13 january 2009
