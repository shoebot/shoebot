import os
import traceback

from time import sleep, time

class Grammar(object):
    ''' 
    A Bot is an interface to receive user commands (through scripts or direct
    calls) and pass them to a canvas for drawing.

    Bae class for all Grammars, contains just the machinery for running the
    grammars, it has only the private API and nothing else, except for
    sb_run which is called to actually run the Bot.
    '''
    def __init__(self, canvas, namespace = None):
        self._canvas = canvas
        self._quit = False
        self._iteration = 0
        self._dynamic = True
        self._speed = None
        self._vars = {}
        self._oldvars = self._vars
        self._namespace = namespace or {}

        input_device = canvas.get_input_device()
        if input_device:
            input_device.set_endpoints(
                key_pressed = self._key_pressed,
                key_released = self._key_released,
                mouse_button_down = self._mouse_button_down,
                mouse_button_up = self._mouse_button_up,
                mouse_pointer_moved = self._mouse_pointer_moved)
        self._input_device = input_device


    def _load_namespace(self, filename = None):
        ''' Export namespace into the user bot '''
        namespace = self._namespace

        from shoebot import data
        for name in dir(data):
            namespace[name] = getattr(data, name)

        for name in dir(self):
            if name[0] != '_':
                namespace[name] = getattr(self, name)

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
        elif iterations is None:
            if self._dynamic:
                return True
            else:
                return False
        if not self._dynamic:
            ### TODO... gtk window needs to run in another thread, that will keep
            ### going until explicitly closed
            print '###TODO'
            return False

        return False

    def _frame_limit(self):
        ''' Limit to framerate, should be called after
            rendering has completed '''
        if self._speed is not None:
            completion_time = time()
            exc_time = completion_time - self._start_time
            sleep_for = (1.0 / self._speed) - exc_time
            if sleep_for > 0:
                sleep(sleep_for)
            self._start_time = completion_time + sleep_for

    ### TODO - Move the logic of setup()/draw()
    ### to bot, but keep the other stuff here
    def _exec_frame(self, source_or_code, limit = False):
        ''' Run single frame of the bot '''
        namespace = self._namespace
        self._canvas.reset_canvas()
        self._set_dynamic_vars()
        if self._iteration == 0:
            # First frame
            exec source_or_code in namespace
            namespace['setup']()
            namespace['draw']()
        else:
            # Subsequent frames
            if self._dynamic:
                namespace['draw']()
            else:
                exec source_or_code in namespace
        
        self._canvas.flush(self._frame)
        if limit:
            self._frame_limit()
        self._frame += 1
        self._iteration += 1

    def sb_run(self, inputcode, iterations = None, run_forever = False, frame_limiter = False):
        '''
        Executes the contents of a Nodebox/Shoebot script
        in current surface's context.
        '''
        source_or_code = ""

        # is it a proper filename?
        if os.path.isfile(inputcode):
            file = open(inputcode, 'rU')
            source_or_code = file.read()
            file.close()
            self._load_namespace(inputcode)
        else:
            # if not, try parsing it as a code string
            source_or_code = inputcode
            self._load_namespace()

        try:
            # if it's a string, it needs compiling first; if it's a file, no action needed
            if isinstance(source_or_code, basestring):
                source_or_code = compile(source_or_code + '\n\n', "shoebot_code", "exec")
            # do the magic            
            if not iterations:
                if run_forever:
                    iterations = None
                else:
                    iterations = 1

            self._start_time = time()

            # First iteration
            self._exec_frame(source_or_code, limit = frame_limiter)

            # Subsequent iterations
            while self._should_run(iterations):
                self._exec_frame(source_or_code, limit = frame_limiter)

            if not run_forever:
                self._quit = True
            self._canvas.sink.finish()

        except NameError:
            # if something goes wrong, print verbose system output
            # maybe this is too verbose, but okay for now
            errmsg = traceback.format_exc()
            print errmsg

    #### Variables
    def _addvar(self, v):
        ''' Sets a new accessible variable.'''
        oldvar = self._oldvars.get(v.name)
        if oldvar is not None:
            if oldvar.compliesTo(v):
                v.value = oldvar.value
        self._vars[v.name] = v
        self._namespace[v.name] = v.value
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
