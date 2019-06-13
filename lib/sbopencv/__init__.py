# Shoebot Computer Vision and Video Library 0.2
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

# this imports cvBlobsLib
try:
    from .blobs.BlobResult import CBlobResult
    from .blobs.Blob import CBlob  # Note: This must be imported in order to destroy blobs and use other methods
except:
    print("Could not load blobs extension, some of the library features will not be available")
    pass

class Movie:

    def __init__(self, path, start=0, stop=None):
        self.path = path
        self.video = hg.cvCreateFileCapture(self.path)

        # these functions don't seem to work at present on my linux system

        # self.fps = hg.cvGetCaptureProperty(self.video, hg.CV_CAP_PROP_FPS)
        # self.n_of_frames = hg.cvGetCaptureProperty(self.video, hg.CV_CAP_PROP_FRAME_COUNT)
        # self.duration = self.n_of_frames/self.fps
        # self.width = hg.cvGetCaptureProperty(self.video, hg.CV_CAP_PROP_FRAME_WIDTH)
        # self.height = hg.cvGetCaptureProperty(self.video, hg.CV_CAP_PROP_FRAME_HEIGHT)
        hg.cvSetCaptureProperty(self.video, hg.CV_CAP_PROP_POS_FRAMES, start)

    def frame(self, t=None, flip=False, bthreshold=128, bthreshmode=0):
        frame = MovieFrame(src=self.video, time=t, flipped=flip, thresh=bthreshold, thmode=bthreshmode)
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

        def release_camera(camera=self.video):
            print(camera)  # this for debugging, do not leave it!!!
            print(dir(camera))  # same as above
            opencv.cvReleaseCapture(camera)
        _ctx.drawing_closed = release_camera

    def frame(self, t=None, flip=False, bthreshold=128, bthreshmode=0):
        try:
            frame = MovieFrame(src=self.video, time=None, flipped=flip, thresh=bthreshold, thmode=bthreshmode)
        except:
            opencv.cvReleaseCapture(self.video)
            raise "could not grab frame, closed camera capture"
        return frame


def camera(cam=0, width=None, height=None):
    return Camera(cam, width, height)


class Image:

    def __init__(self, path=None):
        self.path = path
        try:
            self.iplimage = hg.cvLoadImage(self.path)
        except:
            raise AttributeError("could not load image file")

    def _data(self):
        return ipl2cairo(self.iplimage)
    data = property(_data)

    def contours(self, threshold=100):
        return findcontours(self.iplimage, threshold)

    def haar(self, classifier):
        return detectHaar(self.iplimage, classifier)


def image(path=None):
    return Image(path)


class MovieFrame:

    def __init__(self, src="", time=None, flipped=False, thresh=128, thmode=0):

        self.src = src
        self.time = time
        self.bthresh = thresh
        self.bthreshmode = thmode
        if self.time:
            hg.cvSetCaptureProperty(self.src, hg.CV_CAP_PROP_POS_FRAMES, self.time)
        self.iplimage = hg.cvQueryFrame(self.src)
        if flipped:
            opencv.cvFlip(self.iplimage, None, 1)
        self.width = self.iplimage.width
        self.height = self.iplimage.height

    def _data(self):
        return ipl2cairo(self.iplimage)
    data = property(_data)

    def _faces(self):
        self.classifier = "haarcascade_frontalface_alt"
        return detectHaar(self.iplimage, self.classifier)
    faces = property(_faces)

    def _blobs(self):
        return Blobs(self)
    blobs = property(_blobs)

    def contours(self, threshold=100):
        return findcontours(self.iplimage, threshold)

    def haar(self, classifier):
        return detectHaar(self.iplimage, classifier)


class Blobs:

    def __init__(self, frame):
        self.blob_image = opencv.cvCloneImage(frame.iplimage)
        self.blob_gray = opencv.cvCreateImage(opencv.cvGetSize(self.blob_image), 8, 1)
        self.blob_mask = opencv.cvCreateImage(opencv.cvGetSize(self.blob_image), 8, 1)
        opencv.cvSet(self.blob_mask, 1)
        opencv.cvCvtColor(self.blob_image, self.blob_gray, opencv.CV_BGR2GRAY)
        # opencv.cvEqualizeHist(self.blob_gray, self.blob_gray)
        # opencv.cvThreshold(self.blob_gray, self.blob_gray, frame.thresh, 255, opencv.CV_THRESH_BINARY)
        # opencv.cvThreshold(self.blob_gray, self.blob_gray, frame.thresh, 255, opencv.CV_THRESH_TOZERO)
        opencv.cvThreshold(self.blob_gray, self.blob_gray, frame.bthresh, 255, frame.bthreshmode)
        # opencv.cvAdaptiveThreshold(self.blob_gray, self.blob_gray, 255, opencv.CV_ADAPTIVE_THRESH_MEAN_C, opencv.CV_THRESH_BINARY_INV)
        self._frame_blobs = CBlobResult(self.blob_gray, self.blob_mask, 100, True)
        self._frame_blobs.filter_blobs(10, 10000)
        self.count = self._frame_blobs.GetNumBlobs()
        self.items = []
        for i in range(self.count):
            self.items.append(self._frame_blobs.GetBlob(i))


class Haarobj:

    def __init__(self, obj):
        self.x = obj.x
        self.y = obj.y
        self.width = obj.width
        self.height = obj.height


# common utility functions

def ipl2cairo(iplimage):
    srcimage = opencv.cvCloneImage(iplimage)
    width = srcimage.width
    height = srcimage.height
    image = opencv.cvCreateImage(opencv.cvGetSize(srcimage), 8, 4)
    opencv.cvCvtColor(srcimage, image, opencv.CV_BGR2BGRA)
    buffer = numpy.fromstring(image.imageData, dtype=numpy.uint32).astype(numpy.uint32)
    buffer.shape = (image.width, image.height)
    opencv.cvReleaseImage(srcimage)
    opencv.cvReleaseImage(image)
    return cairo.ImageSurface.create_for_data(buffer, cairo.FORMAT_RGB24, width, height, width * 4)


def detectHaar(iplimage, classifier):
    srcimage = opencv.cvCloneImage(iplimage)
    grayscale = opencv.cvCreateImage(opencv.cvGetSize(srcimage), 8, 1)
    opencv.cvCvtColor(srcimage, grayscale, opencv.CV_BGR2GRAY)
    storage = opencv.cvCreateMemStorage(0)
    opencv.cvClearMemStorage(storage)
    opencv.cvEqualizeHist(grayscale, grayscale)
    try:
        cascade = opencv.cvLoadHaarClassifierCascade(os.path.join(os.path.dirname(__file__), classifier + ".xml"), opencv.cvSize(1, 1))
    except:
        raise AttributeError("could not load classifier file")
    objs = opencv.cvHaarDetectObjects(grayscale, cascade, storage, 1.2, 2, opencv.CV_HAAR_DO_CANNY_PRUNING, opencv.cvSize(50, 50))
    objects = []
    for obj in objs:
        objects.append(Haarobj(obj))
    opencv.cvReleaseImage(srcimage)
    opencv.cvReleaseImage(grayscale)
    opencv.cvReleaseMemStorage(storage)
    return objects


def findcontours(iplimage, threshold=100):
    srcimage = opencv.cvCloneImage(iplimage)
    # create the storage area and bw image
    grayscale = opencv.cvCreateImage(opencv.cvGetSize(srcimage), 8, 1)
    opencv.cvCvtColor(srcimage, grayscale, opencv.CV_BGR2GRAY)
    # threshold
    opencv.cvThreshold(grayscale, grayscale, threshold, 255, opencv.CV_THRESH_BINARY)
    storage = opencv.cvCreateMemStorage(0)
    opencv.cvClearMemStorage(storage)
    # find the contours
    nb_contours, contours = opencv.cvFindContours(grayscale, storage)
    # comment this out if you do not want approximation
    contours = opencv.cvApproxPoly(contours, opencv.sizeof_CvContour, storage, opencv.CV_POLY_APPROX_DP, 3, 1)
    # next line is for ctypes-opencv
    # contours = opencv.cvApproxPoly (contours, opencv.sizeof(opencv.CvContour), storage, opencv.CV_POLY_APPROX_DP, 3, 1)
    conts = []
    for cont in contours.hrange():
        points = []
        for pt in cont:
            points.append((pt.x, pt.y))
        conts.append(points)
    opencv.cvReleaseMemStorage(storage)
    opencv.cvReleaseImage(srcimage)
    opencv.cvReleaseImage(grayscale)
    return (nb_contours, conts)
