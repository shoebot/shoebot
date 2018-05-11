# Shoebot Video Library 0.2
# Copyright: HVA - Hermanitos Verdes Architetti, 2009
# licenSe: LGPL
import cairo
import numpy
import opencv
from opencv import highgui as hg
import os

__author__ = "Francesco Fantoni"
__version__ = "0.2"
__copyright__ = "Copyright (c) 2009, HVA - Hermanitos Verdes Architetti"
__license__ = "lgpl"


class SBVideoError(RuntimeError):
    pass


class Movie:

    def __init__(self, path, start=0, stop=None):
        self.path = path
        self.video = hg.cvCreateFileCapture(self.path)
        if self.video is None:
            raise SBVideoError("Could not open stream %s" % self.path)

        # these functions don't seem to work at present on my linux system

        # self.fps = hg.cvGetCaptureProperty(self.video, hg.CV_CAP_PROP_FPS)
        # self.n_of_frames = hg.cvGetCaptureProperty(self.video, hg.CV_CAP_PROP_FRAME_COUNT)
        # self.duration = self.n_of_frames/self.fps
        # self.width = hg.cvGetCaptureProperty(self.video, hg.CV_CAP_PROP_FRAME_WIDTH)
        # self.height = hg.cvGetCaptureProperty(self.video, hg.CV_CAP_PROP_FRAME_HEIGHT)
        hg.cvSetCaptureProperty(self.video, hg.CV_CAP_PROP_POS_FRAMES, start)

    def frame(self, t=None):
        frame = MovieFrame(src=self.video, time=t)
        return frame


def movie(path, start=0, stop=None):
    return Movie(path, start, stop)


class Camera:

    def __init__(self, cam=0, width=None, height=None):
        self.path = cam
        self.video = hg.cvCreateCameraCapture(self.path)
        if width:
            hg.cvSetCaptureProperty(self.video, hg.CV_CAP_PROP_FRAME_WIDTH, width)
        if height:
            hg.cvSetCaptureProperty(self.video, hg.CV_CAP_PROP_FRAME_HEIGHT, height)

    def frame(self, t=None):
        frame = MovieFrame(src=self.video, time=None)
        return frame


def camera(cam=0, width=None, height=None):
    return Camera(cam, width, height)


class MovieFrame:

    def __init__(self, src="", time=None):

        self.src = src
        self.time = time
        if self.time:
            hg.cvSetCaptureProperty(self.src, hg.CV_CAP_PROP_POS_FRAMES, self.time)
        self.iplimage = hg.cvQueryFrame(self.src)
        self.width = self.iplimage.width
        self.height = self.iplimage.height
        self.image = opencv.cvCreateImage(opencv.cvGetSize(self.iplimage), 8, 4)
        opencv.cvCvtColor(self.iplimage, self.image, opencv.CV_BGR2BGRA)
        self.buffer = numpy.fromstring(self.image.imageData, dtype=numpy.uint32).astype(numpy.uint32)
        self.buffer.shape = (self.image.width, self.image.height)
        self.time = hg.cvGetCaptureProperty(self.src, hg.CV_CAP_PROP_POS_MSEC)

    def _data(self):
        return cairo.ImageSurface.create_for_data(self.buffer, cairo.FORMAT_RGB24, self.width, self.height, self.width * 4)

    data = property(_data)

    def detectObject(self, classifier):
        self.grayscale = opencv.cvCreateImage(opencv.cvGetSize(self.iplimage), 8, 1)
        opencv.cvCvtColor(self.iplimage, self.grayscale, opencv.CV_BGR2GRAY)
        self.storage = opencv.cvCreateMemStorage(0)
        opencv.cvClearMemStorage(self.storage)
        opencv.cvEqualizeHist(self.grayscale, self.grayscale)

        try:
            self.cascade = opencv.cvLoadHaarClassifierCascade(os.path.join(os.path.dirname(__file__), classifier+".xml"),opencv.cvSize(1, 1))
        except:
            raise AttributeError, "could not load classifier file"

        self.objects = opencv.cvHaarDetectObjects(self.grayscale, self.cascade, self.storage, 1.2, 2, opencv.CV_HAAR_DO_CANNY_PRUNING, opencv.cvSize(50, 50))

        return self.objects

    def _faces(self):
        classifier = "haarcascade_frontalface_alt"
        return self.detectObject(classifier)
    faces = property(_faces)


class objecttest:
    def __init__(self, i):
        self.x = 1 * i
        self.y = 1 * i
        self.width = 10 * i
        self.height = 10 * i
