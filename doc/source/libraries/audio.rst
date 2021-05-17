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
