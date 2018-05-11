import atexit
import threading
import numpy as np
from pysoundcard import InputStream
from pysoundcard import device_info
from fuzzywuzzy import fuzz


BUFF_LENGTH = 1024
CHANNELS = 2
NUM_SAMPLES = 512


def fft_bandpassfilter(data, fs, lowcut, highcut):
    """
    http://www.swharden.com/blog/2009-01-21-signal-filtering-with-python/#comment-16801
    """
    fft = np.fft.fft(data)
    # n = len(data)
    # timestep = 1.0 / fs
    # freq = np.fft.fftfreq(n, d=timestep)
    bp = fft.copy()

    # Zero out fft coefficients
    # bp[10:-10] = 0

    # Normalise
    # bp *= real(fft.dot(fft))/real(bp.dot(bp))

    bp *= fft.dot(fft) / bp.dot(bp)

    # must multipy by 2 to get the correct amplitude
    ibp = 12 * np.fft.ifft(bp)
    return ibp

    # for i in range(len(bp)):
    #     if freq[i] >= highcut or freq[i] < lowcut:
    #         bp[i] = 0

    # ibp = np.fft.ifft(bp)
    # ibp = 2.0 * np.fft.ifft(bp)
    # print ibp
    # return ibp


def flatten_fft(scale=1.0):
    """
    Produces a nicer graph, I'm not sure if this is correct
    """
    _len = len(audio.spectrogram)
    for i, v in enumerate(audio.spectrogram):
        yield scale * (i * v) / _len


def scaled_fft(fft, scale=1.0):
    """
    Produces a nicer graph, I'm not sure if this is correct
    """
    data = np.zeros(len(fft))
    for i, v in enumerate(fft):
        data[i] = scale * (i * v) / NUM_SAMPLES

    return data


def triple(spectrogram):
    # c = spectrogram.copy()
    # c.resize(3, 255 / 3)
    # return c
    bass = spectrogram[0:85]
    mid = spectrogram[85:-85]
    treble = spectrogram[-85:-1]

    return bass, mid, treble


def fuzzydevices(match='', min_ratio=30):
    device_ratios = []
    for device in device_info():
        ratio = fuzz.partial_ratio(match, device['name'])
        if ratio > min_ratio:
            device_ratios.append((ratio, device))

    for ratio, device in sorted(device_ratios, key=lambda ratio_device: (ratio_device[0])):
        yield device


def firstfuzzydevice(match=''):
    devices = list(fuzzydevices(match, 0))
    return devices[0]


class AudioException(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        return self.msg


class AudioThread(threading.Thread):
    def __init__(self):
        # TODO - This could be a bit less dumb, and only run
        #        bandpass (or other) filters if they are actually used
        super(self.__class__, self).__init__()

        self.daemon = True

        self.streams = {}
        self.running = False

        self._spectrogram = np.zeros(NUM_SAMPLES)
        self._bandpassed = np.zeros(NUM_SAMPLES)

    def settings(self, **kwargs):
        if self.running:
            raise AudioException('Audio is already running')

    def run(self):
        with InputStream(samplerate=44100, blocksize=16) as s:
            while self.running:
                vec = s.read(NUM_SAMPLES)
                # Downsample to mono
                mono_vec = vec.sum(-1) / float(s.channels)
                self._spectrogram = np.fft.fft(mono_vec)
                self._bandpassed = fft_bandpassfilter(self.spectrogram, 44010, 100, 20)

    def autostart(self):
        if not self.running:
            self.running = True
            self.start()
            atexit.register(self.quit)

    def quit(self):
        """
        Shutdown the audio thread
        """
        if self.running:
            self.running = False
            self.join()

    @property
    def spectrogram(self):
        self.autostart()
        return self._spectrogram

    @property
    def bandpassed(self):
        self.autostart()
        return self._bandpassed


audio = AudioThread()
