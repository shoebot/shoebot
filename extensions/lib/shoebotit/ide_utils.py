"""
Utility functions for IDEs and plugins.

The install process should copy this file to the same location as shoebot.

Functions here are expected to work not need shoebot in the library path.

"""

try:
    import queue
except ImportError:
    import Queue as queue

import base64
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


class ShoebotProcess(object):
    def __init__(self, code, use_socketserver, show_varwindow, use_fullscreen, title, cwd=None, handle_stdout=None, handle_stderr=None, sbot=None):
        # start with -w for window -l for shell'
        command = [sbot, '-wl', '-t%s - Shoebot on gedit' % title]

        if use_socketserver:
            command.append('-s')

        if not show_varwindow:
            command.append('-dv')

        if use_fullscreen:
            command.append('-f')
        
        command.append(code)

        # Setup environment so shoebot directory is first
        _env = os.environ.copy()
        if sbot:
            _env['PATH'] = os.path.realpath(os.path.dirname(sbot)) + os.pathsep + os.environ.get('PATH', '')
        else:
            print('no sbot!')

        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, close_fds=True, shell=False, cwd=cwd, close_fds=os.name != 'nt')

        self.running = True

        # Launch the asynchronous readers of the process' stdout and stderr.
        self.stdout_queue = queue.Queue()
        self.stdout_reader = AsynchronousFileReader(self.process.stdout, self.stdout_queue)
        self.stdout_reader.start()
        self.stderr_queue = queue.Queue()
        self.stderr_reader = AsynchronousFileReader(self.process.stderr, self.stderr_queue)
        self.stderr_reader.start()

        self.handle_stdout = handle_stdout
        self.handle_stderr = handle_stderr
        self.changed_handler_id = None

        self.code = code.rstrip('\n')

    def live_code_load(self, source):
        source = source.rstrip('\n')
        if source != self.code:
            self.code = source
            self.send_command("load_base64", source)

    def pause(self):
        self.send_command('pause')

    def send_command(self, cmd, *args):
        if args:
            self.process.stdin.write(bytes(cmd, "utf-8") + b" " + base64.b64encode(bytes(", ".join(args), "utf-8")))
        else:
            self.process.stdin.write(bytes(cmd, "utf-8"))
        self.process.stdin.write(b"\n")
        self.process.stdin.flush()

    def close(self):
        """
        Close outputs of process.
        """
        self.process.stdout.close()
        self.process.stderr.close()
        self.running = False

    def get_output(self):
        """
        :yield: stdout_line, stderr_line, running

        Generator that outputs lines captured from stdout and stderr

        These can be consumed to output on a widget in an IDE
        """

        if self.process.poll() is not None:
            self.close()
            yield None, None

        while not (self.stdout_queue.empty() and self.stderr_queue.empty()):
            if not self.stdout_queue.empty():
                line = self.stdout_queue.get().decode('utf-8')
                yield line, None

            if not self.stderr_queue.empty():
                line = self.stderr_queue.get().decode('utf-8')
                yield None, line


def get_example_dir():
    return _example_dir


def find_example_dir():
    """
    Find examples dir .. a little bit ugly..
    """

    # Needs to run in same python env as shoebot (may be different to gedits)

    code = "from pkg_resources import resource_filename, Requirement; print resource_filename(Requirement.parse('shoebot'), 'share/shoebot/examples/')"
    cmd = ["python", "-c", code]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output, errors = p.communicate()
    if errors:
        print('Could not find shoebot examples')
        print('Errors: {0}'.format(errors))
        return None
    else:
        examples_dir = output.decode('utf-8').strip()
        if os.path.isdir(examples_dir):
            return examples_dir
        else:
            print('Could not find shoebot examples at {0}'.format(examples_dir))


def make_readable_filename(fn):
    """
    Change filenames for display in the menu.
    """
    return os.path.splitext(fn)[0].replace('_', ' ').capitalize()


_example_dir = find_example_dir()
