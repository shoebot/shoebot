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
import collections
import os
import subprocess
import sys
import textwrap
import threading
import time
import uuid
import re

PY3 = sys.version_info[0] == 3

CMD_LOAD_BASE64 = 'load_base64'

RESPONSE_CODE_OK = "CODE_OK"
RESPONSE_REVERTED = "REVERTED"


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


class CommandResponse(collections.namedtuple("CommandResponse", ['cmd', 'cookie', 'status', 'info'])):
    __slots__ = ()

    def __new__(cls, cmd, cookie, status=None, info=[]):
        return super(CommandResponse, cls).__new__(cls, cmd, cookie, status, info)

    def __str__(self):
        return 'cmd: {0} info{1}'.format(self.cmd, self.info)


class ShoebotProcess(object):
    """
    Runs an instance of Shoebot

    use send_command to control the instance, CommandResponse objects
    come back in the response_queue

    """
    def __init__(self, source, use_socketserver, show_varwindow, use_fullscreen, verbose, title, cwd=None, handle_stdout=None, handle_stderr=None, sbot=None):
        # start with -w for window -l for shell'
        command = [sbot, '-wl', '-t%s' % title]

        if use_socketserver:
            command.append('-s')

        if not show_varwindow:
            command.append('-dv')

        if use_fullscreen:
            command.append('-f')

        if verbose:
            command.append("-V")

        command.append(source)

        # Setup environment so shoebot directory is first
        _env = os.environ.copy()
        if sbot:
            _env.update(
                PATH=os.path.realpath(os.path.dirname(sbot)) + os.pathsep + os.environ.get('PATH', ''),
                # PYTHONUNBUFFERED='1'
            )
        else:
            print('no sbot!')

        startupinfo = subprocess.STARTUPINFO()
        if os.name == 'nt':
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=os.name != 'nt', shell=False, cwd=cwd, startupinfo=startupinfo)

        self.running = True

        self.responses = {}

        def response_handler(line):
            line = line.decode('utf-8').rstrip()
            for cookie, response in list(self.responses.items()):
                if line.startswith(cookie):
                    pattern = r"^" + cookie + "\s?(?P<status>(.*?))[\:>](?P<info>.*)"

                    match = re.match(pattern, line)
                    d = match.groupdict()
                    status = d.get('status')
                    info = d.get('info')

                    if not response.status and status:
                        self.responses[cookie] = response = \
                            CommandResponse(response.cmd, cookie, response.status or status, response.info)

                    response.info.append(info)

                    # If delimiter was '>' there are more lines
                    # If delimiter was ':' request is complete
                    delimiter = re.match('.*([:>])', line).group(1)
                    if delimiter == ':':
                        del self.responses[cookie]
                        self.response_queue.put_nowait(response)

                    return True  # response was handled

        # Launch the asynchronous readers of the process' stdout and stderr.
        self.stdout_queue = queue.Queue()
        self.stdout_reader = AsynchronousFileReader(self.process.stdout, self.stdout_queue, althandler=response_handler)
        self.stdout_reader.start()
        self.stderr_queue = queue.Queue()
        self.stderr_reader = AsynchronousFileReader(self.process.stderr, self.stderr_queue)
        self.stderr_reader.start()

        self.response_queue = queue.Queue()

        self.handle_stdout = handle_stdout
        self.handle_stderr = handle_stderr
        self.changed_handler_id = None

        self.source = source.rstrip('\n')

        self.setup_io()

    def setup_io(self):
        # Turn off user prompts
        self.send_command('prompt', 'off')
        self.send_command('')

        # Make responses single lines
        self.send_command("escape_nl")
        self.send_command('')

    def live_source_load(self, source):
        """
        Send new source code to the bot

        :param source:
        :param good_cb: callback called if code was good
        :param bad_cb: callback called if code was bad (will get contents of exception)
        :return:
        """
        source = source.rstrip('\n')
        if source != self.source:
            self.source = source
            b64_source = base64.b64encode(source.encode('utf-8')).decode('utf-8')
            self.send_command(CMD_LOAD_BASE64, b64_source)

    def pause(self):
        self.send_command('pause')

    def send_command(self, cmd, *args):
        """
        :param cmd:
        :param args:
        :return:
        """
        cookie = f"{uuid.uuid4()}"
        response = CommandResponse(cmd, cookie, None, info=[])
        self.responses[cookie] = response
        data = ' '.join([cmd, *args, f'cookie={cookie}\n'])

        self.process.stdin.write(data.encode('utf-8'))
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

    def get_command_responses(self):
        """
        Get responses to commands sent
        """
        if not self.response_queue.empty():
            yield None
        while not self.response_queue.empty():
            line = self.response_queue.get()
            if line is not None:
                yield line


def get_example_dir():
    return _example_dir


def find_example_dir():
    """
    Find examples dir .. a little bit ugly..
    """
    # Replace %s with directory to check for shoebot menus.
    code_stub = textwrap.dedent("""
    from pkg_resources import resource_filename, Requirement, DistributionNotFound
    try:
        print(resource_filename(Requirement.parse('shoebot'), '%s'))
    except DistributionNotFound:
        pass

    """)

    # Needs to run in same python env as shoebot (may be different to gedits)
    code = code_stub % 'share/shoebot/examples'
    cmd = ["python", "-c", code]
    startupinfo = subprocess.STARTUPINFO()
    if os.name == 'nt':
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
    output, errors = p.communicate()
    if errors:
        print('Shoebot experienced errors searching for install and examples.')
        print('Errors:\n{0}'.format(errors.decode('utf-8')))
        return None
    else:
        examples_dir = output.decode('utf-8').strip()
        if os.path.isdir(examples_dir):
            return examples_dir

        # If user is running 'setup.py develop' then examples could be right here
        # code = "from pkg_resources import resource_filename, Requirement; print resource_filename(Requirement.parse('shoebot'), 'examples/')"
        code = code_stub % 'examples/'
        cmd = ["python", "-c", code]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, startupinfo=startupinfo)
        output, errors = p.communicate()
        examples_dir = output.decode('utf-8').strip()
        if os.path.isdir(examples_dir):
            return examples_dir

        if examples_dir:
            print('Shoebot could not find examples at: {0}'.format(examples_dir))
        else:
            print('Shoebot could not find install dir and examples.')


def make_readable_filename(fn):
    """
    Change filenames for display in the menu.
    """
    return os.path.splitext(fn)[0].replace('_', ' ').capitalize()


_example_dir = find_example_dir()
