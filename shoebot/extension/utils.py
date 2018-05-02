import Queue as queue
import os
import threading
import time


def make_readable_filename(fn):
    """
    Change filenames for display in the menu.
    """
    return os.path.splitext(fn)[0].replace('_', ' ').capitalize()


class AsynchronousFileReader(threading.Thread):
    """
    Helper class to implement asynchronous reading of a file
    in a separate thread. Pushes read lines on a queue to
    be consumed in another thread.
    """

    def __init__(self, fd, q, althandler=None):
        assert isinstance(q, queue.Queue)
        assert callable(fd.readline)
        threading.Thread.__init__(self)
        self._fd = fd
        self._queue = q
        self._althandler = althandler

    def run(self):
        """
        The body of the tread: read lines and put them on the queue.
        """
        try:
            for line in iter(self._fd.readline, False):
                if line is not None:
                    if self._althandler:
                        if self._althandler(line):
                            # If the althandler returns True
                            # then don't process this as usual
                            continue
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
