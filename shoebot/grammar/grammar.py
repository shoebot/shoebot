import os
from livecode import LiveExecution
import traceback

from time import sleep, time
from var_listener import VarListener
from shoebot.data import Variable
from shoebot.util import flushfile

import copy
import linecache
import sys

sys.stdout = flushfile(sys.stdout)
sys.stderr = flushfile(sys.stderr)


class Grammar(object):
    ''' 
    A Bot is an interface to receive user commands (through scripts or direct
    calls) and pass them to a canvas for drawing.

    Bae class for all Grammars, contains just the machinery for running the
    grammars, it has only the private API and nothing else, except for
    run which is called to actually run the Bot.
    '''
    def __init__(self, canvas, namespace = None, vars = None):
        self._canvas = canvas
        self._quit = False
        self._iteration = 0
        self._dynamic = True
        self._speed = 60.0
        self._vars = vars or {}
        self._oldvars = self._vars
        self._namespace = namespace or {}

        self._var_listeners = []

        self._executor = None

        input_device = canvas.get_input_device()
        if input_device:
            input_device.set_callbacks(
                key_pressed = self._key_pressed,
                key_released = self._key_released,
                mouse_button_down = self._mouse_button_down,
                mouse_button_up = self._mouse_button_up,
                mouse_pointer_moved = self._mouse_pointer_moved)
        self._input_device = input_device

    def _load_namespace(self, filename = None):
        ''' Export namespace into the user bot
        :param filename: Will be set to __file__ in the namespace
        '''
        namespace = self._namespace

        from shoebot import data
        for name in dir(data):
            namespace[name] = getattr(data, name)

        for name in dir(self):
            if name[0] != '_':
                namespace[name] = getattr(self, name)

        namespace['_ctx'] = self  # Used in older nodebox scripts.
        namespace['__file__'] = filename
        self._namespace = namespace


    #### Execute a single frame

    def _should_run(self, iterations):
        ''' Return False if bot should quit '''

        iteration = self._iteration
        if iteration == 0:
            # First frame always runs
            return True
        if self._quit:
            return False
        if iterations:
            if iteration < iterations:
                return True
        elif len(self._vars) > 0:
            # Vars have been added in script
            return True
        elif iterations is None:
            if self._dynamic:
                return True
            else:
                return False
            return True
        if not self._dynamic:
            ### TODO... gtk window needs to run in another thread, that will keep
            ### going until explicitly closed
            return False

        return False

    def _frame_limit(self):
        ''' Limit to framerate, should be called after
            rendering has completed '''
        if self._speed:
            completion_time = time()
            exc_time = completion_time - self._start_time
            sleep_for = (1.0 / self._speed) - exc_time
            if sleep_for > 0:
                sleep(sleep_for)
            self._start_time = completion_time + sleep_for

    ### TODO - Move the logic of setup()/draw()
    ### to bot, but keep the other stuff here
    def _exec_frame(self, limit = False):
        ''' Run single frame of the bot

        :param source_or_code: path to code to run, or actual code.
        :param limit: Time a frame should take to run (float - seconds)
        '''
        namespace = self._namespace
        if self._speed != 0:
            self._canvas.reset_canvas()
        self._set_dynamic_vars()
        if self._iteration == 0:
            # First frame
            self._executor.run()
            # run setup and draw
            # (assume user hasn't live edited already)
            namespace['setup']()
            namespace['draw']()
        else:
            # Subsequent frames
            if self._dynamic and self._speed != 0:
                with self._executor.run_context() as (known_good, source, ns):
                    # Code in main block may redefine 'draw'
                    self._executor.reload_functions()
                    if not known_good:
                        with VarListener.batch(self._vars, self._oldvars, self._var_listeners):
                            self._oldvars.clear()

                            # Re-run the function body - ideally this would only
                            # happen if the body had actually changed
                            # - Or perhaps if the line included a variable declatation
                            exec source in ns

                    ns['draw']()
            else:
                self._executor.run()
        
        self._canvas.flush(self._frame)
        if limit:
            self._frame_limit()

        # Can set speed to go backwards using the shell if you really want
        # or pause by setting speed == 0
        if self._speed > 0:
            self._frame += 1
        elif self._speed < 0:
            self._frame -= 1

        self._iteration += 1

    def _simple_traceback(self, ex, source):
        """
        Format traceback, showing line number and surrounding source.
        """
        exc_type, exc_value, exc_tb = sys.exc_info()
        exc = traceback.format_exception(exc_type, exc_value, exc_tb)

        source_arr = source.splitlines()

        # Defaults...
        exc_location = exc[-2]
        for i, err in enumerate(exc):
            if 'exec source_or_code in namespace' in err:
                exc_location = exc[i+1]
                break

        # extract line number from traceback
        fn=exc_location.split(',')[0][8:-1]
        line_number = int(exc_location.split(',')[1].replace('line', '').strip())

        # Build error messages

        err_msgs = []

        # code around the error
        err_where = ' '.join(exc[i-1].split(',')[1:]).strip()   # 'line 37 in blah"
        err_msgs.append('Error in the Shoebot script at %s:' % err_where)
        for i in xrange(max(0, line_number-5), line_number):
            if fn == "shoebot_code":
                line = source_arr[i]
            else:
                line = linecache.getline(fn, i+1)
            err_msgs.append('%s: %s' % (i+1, line.rstrip()))
        err_msgs.append('  %s^ %s' % (len(str(i)) * ' ', exc[-1].rstrip()))

        err_msgs.append('')
        # traceback
        err_msgs.append(exc[0].rstrip())
        for err in exc[3:]:
            err_msgs.append(err.rstrip())

        return '\n'.join(err_msgs)


    def run(self, inputcode, iterations = None, run_forever = False, frame_limiter = False, verbose = False):
        '''
        Executes the contents of a Nodebox/Shoebot script
        in current surface's context.

        :param inputcode: path to shoebot file or whole source code
        :param iterations: maximum amount of frames to run
        :param run_forever: if True will run until the user quits the bot
        :param frame_limiter: Time a frame should take to run (float - seconds)
        '''
        source = None
        filename = None

        try:
            if os.path.isfile(inputcode):
                source = open(inputcode)
                filename = inputcode
            elif isinstance(inputcode, basestring):
                filename = 'shoebot_code'
                source = inputcode
            
            self._executor = LiveExecution(source, ns=self._namespace, filename=filename)
            self._load_namespace(filename)
            
            # do the magic   
            if not iterations:
                if run_forever:
                    iterations = None
                else:
                    iterations = 1

            self._start_time = time()

            with self._executor.run_context():
                # First iteration
                self._exec_frame(limit = frame_limiter)
                self._initial_namespace = copy.copy(self._namespace) # Stored so script can be rewound

                # Subsequent iterations
                while self._should_run(iterations):
                    self._exec_frame(limit = frame_limiter)

            if not run_forever:
                self._quit = True
            self._canvas.finished = True
            self._canvas.sink.finish()

        except Exception as e:
            # this makes KeyboardInterrupts still work
            # if something goes wrong, print verbose system output
            # maybe this is too verbose, but okay for now

            import sys
            if verbose:
                errmsg = traceback.format_exc()
            else:
                errmsg = self._simple_traceback(e, self._executor.known_good or '')
            print >> sys.stderr, errmsg

    def finish(self):
        ## For use when using shoebot as a module
        ## TODO: Not used when running as a bot, possibly should not be available in
        ## this case
        self._canvas.flush(self._frame)
        self._canvas.sink.finish()

    #### Variables
    def _addvar(self, v):
        ''' Sets a new accessible variable.

        :param v: Variable.
        '''
        oldvar = self._oldvars.get(v.name)
        if oldvar is not None:
            if isinstance(oldvar, Variable):
                if oldvar.compliesTo(v):
                    v.value = oldvar.value
            else:
                # Set from commandline
                v.value = v.sanitize(oldvar)
        else:
            for listener in self._var_listeners:
                listener.var_added(v)
        self._vars[v.name] = v
        self._namespace[v.name] = v.value
        self._oldvars[v.name] = v
        return v

    def _findvar(self, name):
        for v in self._oldvars:
            if v.name == name:
                return v
        return None

    #### For override by implementing grammars: ####
    def _mouse_button_down(self, button):
        pass

    def _mouse_button_up(self, button):
        pass

    def _mouse_pointer_moved(self, x, y):
        pass

    def _key_pressed(self, key, keycode):
        pass

    def _key_released(self, key, keycode):
        pass
