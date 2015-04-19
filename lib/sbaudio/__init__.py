try:
    import pysoundcard
except ImportError:
    print('imstall pysoundcard with "pip install pysoundcard"')

from pysoundcard import Stream, continue_flag

import atexit
import time
import threading
import math
import numpy as np
import struct

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


class AudioThread(threading.Thread):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.quit = False
        
        self.spectrogram = np.zeros(BUFF_LENGTH)
        self.bandpassed = np.zeros(BUFF_LENGTH)
        
        self.daemon = True

    def run(self):
        with Stream(sample_rate=44100, block_length=16) as s:
            while self.quit is False:
                vec = s.read(NUM_SAMPLES)

                # Downsample to mono
                mono_vec = vec.sum(-1) / float(s.input_channels)

                self.spectrogram = np.fft.fft(mono_vec)

                #self.bandpassed = fft_bandpassfilter(self.spectrogram, 44010, 100, 20)
                #print random()

def quit():
    audio.quit = True
    audio.join()

audio = AudioThread()
audio.start()

atexit.register(quit)
