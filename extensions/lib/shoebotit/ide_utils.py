"""
Utility functions for IDEs and plugins.

The install process should copy this file to the same location as shoebot.

Functions here are expected to work not need shoebot in the library path.

"""

import queue
import os
import subprocess
import threading
import time


class AsynchronousFileReader(threading.Thread):
    """
    Helper class to implement asynchronous reading of a file
    in a separate thread. Pushes read lines on a queue to
    be consumed in another thread.
    """

    def __init__(self, fd, q):
        assert isinstance(q, queue.Queue)
        assert callable(fd.readline)
        threading.Thread.__init__(self)
        self._fd = fd
        self._queue = q

    def run(self):
        """
        The body of the tread: read lines and put them on the queue.
        """
        try:
            for line in iter(self._fd.readline, False):
                self._queue.put(line)
                if not line:
                    time.sleep(0.1)
        except ValueError:  # This can happen if we are closed during readline - TODO - better fix.
            if not self._fd.closed:
                raise

    def eof(self):
        """
        Check whether there is no more content to expect.
        """
        return (not self.is_alive()) and self._queue.empty() or self._fd.closed


def get_example_dir():
    return _example_dir


def find_example_dir():
    """
    Find examples dir .. a little bit ugly..
    """

    # Needs to run in same python env as shoebot (may be different to gedits)
    cmd = ["python", "-c", "import sys; print '{}/share/shoebot/examples/'.format(sys.prefix)"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output, errors = p.communicate()
    if errors:
        print('Could not find shoebot examples')
        print('Errors: {}'.format(errors))
        return None
    else:
        examples_dir = output.decode('utf-8').strip()
        if os.path.isdir(examples_dir):
            return examples_dir
        else:
            print('Could not find shoebot examples at {}'.format(examples_dir))


def make_readable_filename(fn):
    """
    Change filenames for display in the menu.
    """
    return os.path.splitext(fn)[0].replace('_', ' ').capitalize()


_example_dir = find_example_dir()