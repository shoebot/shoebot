from pysoundcard import Stream, continue_flag
import procname

import atexit
import collections
import time
import threading
import math
import numpy as np
import struct

from pysoundcard import devices
from fuzzywuzzy import fuzz


BUFF_LENGTH = 1024
CHANNELS = 2
NUM_SAMPLES = 512

def scaled_fft(fft, scale = 1.0):
    """
    Produces a nicer graph, I'm not sure if this is correct
    """
    data = np.zeros(len(fft))
    for i, v in enumerate(fft):
         data[i] = scale * (i * v) / NUM_SAMPLES
         
    return data

def triple(spectrogram):
    #c = spectrogram.copy()
    #c.resize(3, 255 / 3)
    #return c
    bass = spectrogram[0:85]
    mid = spectrogram[85:-85]
    treble = spectrogram[-85:-1]

    return bass, mid, treble


def fuzzydevices(match='', min_ratio=30):
    device_ratios = []
    for device in devices():
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
        super(self.__class__, self).__init__()
        
        self._spectrogram = np.zeros(BUFF_LENGTH)
        self._bandpassed = np.zeros(BUFF_LENGTH)
        
        self.daemon = True

        self.streams = {}
        self.running = False

    def settings(self, **kwargs):
        if self.running:
            raise AudioException('Audio is already running')

    def run(self):
        with Stream(sample_rate=44100, block_length=16) as s:
            while self.running:
                vec = s.read(NUM_SAMPLES)

                # Downsample to mono
                mono_vec = vec.sum(-1) / float(s.input_channels)

                self._spectrogram = np.fft.fft(mono_vec)

                #self.bandpassed = fft_bandpassfilter(self.spectrogram, 44010, 100, 20)
                #print random()

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

procname.setprocname('looper')
audio = AudioThread()

