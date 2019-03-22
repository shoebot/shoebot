import copy
import os
import sys
import traceback
from time import sleep, time

from livecode import LiveExecution
from shoebot.core.events import next_event, QUIT_EVENT, SOURCE_CHANGED_EVENT, event_is, SET_WINDOW_TITLE
from shoebot.core.var_listener import VarListener
from shoebot.data import Variable
from shoebot.grammar.format_traceback import simple_traceback
from shoebot.util import flushfile

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

    def __init__(self, canvas, namespace=None, vars=None):
        self._canvas = canvas
        self._quit = False
        self._dynamic = True
        self._speed = 60.0
        self._vars = vars or {}
        self._oldvars = self._vars
        self._namespace = namespace or {}

        input_device = canvas.get_input_device()
        if input_device:
            input_device.set_callbacks(
                key_pressed=self._key_pressed,
                key_released=self._key_released,
                mouse_button_down=self._mouse_button_down,
                mouse_button_up=self._mouse_button_up,
                mouse_pointer_moved=self._mouse_pointer_moved)
        self._input_device = input_device

    def _load_namespace(self, namespace, filename=None):
        """
        Initialise bot namespace with info in shoebot.data

        :param filename: Will be set to __file__ in the namespace
        """
        from shoebot import data
        for name in dir(data):
            namespace[name] = getattr(data, name)

        for name in dir(self):
            if name[0] != '_':
                namespace[name] = getattr(self, name)

        namespace['_ctx'] = self  # Used in older nodebox scripts.
        namespace['__file__'] = filename

    #### Execute a single frame

    def _should_run(self, iteration, max_iterations):
        ''' Return False if bot should quit '''
        if iteration == 0:
            # First frame always runs
            return True
        if max_iterations:
            if iteration < max_iterations:
                return True
        elif max_iterations is None:
            if self._dynamic:
                return True
            else:
                return False
            return True
        if not self._dynamic:
            return False

        return False

    def _frame_limit(self, start_time):
        """
        Limit to framerate, should be called after
        rendering has completed

        :param start_time: When execution started
        """
        if self._speed:
            completion_time = time()
            exc_time = completion_time - start_time
            sleep_for = (1.0 / abs(self._speed)) - exc_time
            if sleep_for > 0:
                sleep(sleep_for)

    ### TODO - Move the logic of setup()/draw()
    ### to bot, but keep the other stuff here
    def _run_frame(self, executor, limit=False, iteration=0):
        """ Run single frame of the bot

        :param source_or_code: path to code to run, or actual code.
        :param limit: Time a frame should take to run (float - seconds)
        """
        #
        # Gets a bit complex here...
        #
        # Nodebox (which we are trying to be compatible with) supports two
        # kinds of bot 'dynamic' which has a 'draw' function and non dynamic
        # which doesn't have one.
        #
        # Dynamic bots:
        #
        # First run:
        # run body and 'setup' if it exists, then 'draw'
        #
        # Later runs:
        # run 'draw'
        #
        # Non Dynamic bots:
        #
        # Just have a 'body' and run once...
        #
        # UNLESS...  a 'var' is changed, then run it again.
        #
        #
        # Livecoding:
        #
        # Code can be 'known_good' or 'tenous' (when it has been edited).
        #
        # If code is tenous and an exception occurs, attempt to roll
        # everything back.
        #
        # Livecoding and vars
        #
        # If vars are added / removed or renamed then attempt to update
        # the GUI

        start_time = time()
        if iteration != 0 and self._speed != 0:
            self._canvas.reset_canvas()
        self._set_dynamic_vars()
        if iteration == 0:
            # First frame
            executor.run()
            # run setup and draw
            # (assume user hasn't live edited already)
            executor.ns['setup']()
            executor.ns['draw']()
            self._canvas.flush(self._frame)
        else:
            # Subsequent frames
            if self._dynamic:
                if self._speed != 0:  # speed 0 is paused, so do nothing
                    with executor.run_context() as (known_good, source, ns):
                        # Code in main block may redefine 'draw'
                        if not known_good:
                            executor.reload_functions()
                            with VarListener.batch(self._vars, self._oldvars, ns):
                                self._oldvars.clear()

                                # Re-run the function body - ideally this would only
                                # happen if the body had actually changed
                                # - Or perhaps if the line included a variable declaration
                                exec source in ns

                        ns['draw']()
                        self._canvas.flush(self._frame)
            else:
                # Non "dynamic" bots
                #
                # TODO - This part is overly complex, before live-coding it
                #        was just exec source in ns ... have to see if it
                #        can be simplified again.
                #
                with executor.run_context() as (known_good, source, ns):
                    if not known_good:
                        executor.reload_functions()
                        with VarListener.batch(self._vars, self._oldvars, ns):
                            self._oldvars.clear()

                            # Re-run the function body - ideally this would only
                            # happen if the body had actually changed
                            # - Or perhaps if the line included a variable declaration
                            exec source in ns
                    else:
                        exec source in ns

                    self._canvas.flush(self._frame)
        if limit:
            self._frame_limit(start_time)

        # Can set speed to go backwards using the shell if you really want
        # or pause by setting speed == 0
        if self._speed > 0:
            self._frame += 1
        elif self._speed < 0:
            self._frame -= 1

    def run(self, inputcode, iterations=None, run_forever=False, frame_limiter=False, verbose=False,
            break_on_error=False):
        '''
        Executes the contents of a Nodebox/Shoebot script
        in current surface's context.

        :param inputcode: Path to shoebot source or string containing source
        :param iterations: None or Maximum amount of frames to run
        :param run_forever: If True then run until user quits the bot
        :param frame_limiter: If True then sleep between frames to respect speed() command.
        '''
        source = None
        filename = None

        if os.path.isfile(inputcode):
            source = open(inputcode).read()
            filename = inputcode
        elif isinstance(inputcode, basestring):
            filename = 'shoebot_code'
            source = inputcode

        self._load_namespace(self._namespace, filename)
        self._executor = executor = LiveExecution(source, ns=self._namespace, filename=filename)

        try:
            if not iterations:
                if run_forever:
                    iterations = None
                else:
                    iterations = 1
            iteration = 0

            event = None

            while iteration != iterations and not event_is(event, QUIT_EVENT):
                # do the magic

                # First iteration
                self._run_frame(executor, limit=frame_limiter, iteration=iteration)
                if iteration == 0:
                    self._initial_namespace = copy.copy(self._namespace)  # Stored so script can be rewound
                iteration += 1

                # Subsequent iterations
                while self._should_run(iteration, iterations) and event is None:
                    iteration += 1
                    self._run_frame(executor, limit=frame_limiter, iteration=iteration)
                    event = next_event()
                    if not event:
                        self._canvas.sink.main_iteration()  # update GUI, may generate events..

                while run_forever:
                    #
                    # Running in GUI, bot has finished
                    # Either -
                    #   receive quit event and quit
                    #   receive any other event and loop (e.g. if var changed or source edited)
                    #
                    while event is None:
                        self._canvas.sink.main_iteration()
                        event = next_event(block=True, timeout=0.05)
                        if not event:
                            self._canvas.sink.main_iteration()  # update GUI, may generate events..

                    if event.type == QUIT_EVENT:
                        break
                    elif event.type == SOURCE_CHANGED_EVENT:
                        # Debounce SOURCE_CHANGED events -
                        # gedit generates two events for changing a single character -
                        # delete and then add
                        while event and event.type == SOURCE_CHANGED_EVENT:
                            event = next_event(block=True, timeout=0.001)
                    elif event.type == SET_WINDOW_TITLE:
                        self._canvas.sink.set_title(event.data)

                    event = None  # this loop is a bit weird...
                    break

        except Exception as e:
            # this makes KeyboardInterrupts still work
            # if something goes wrong, print verbose system output
            # maybe this is too verbose, but okay for now

            import sys
            if verbose:
                errmsg = traceback.format_exc()
            else:
                errmsg = simple_traceback(e, executor.known_good or '')
            print >> sys.stderr, errmsg
            if break_on_error:
                raise

    def finish(self):
        ## For use when using shoebot as a module
        ## TODO: Not used when running as a bot, possibly should not be available in
        ## this case
        self._canvas.flush(self._frame)

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
            for listener in VarListener.listeners:
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
