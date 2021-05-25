from __future__ import print_function

import copy
import dataclasses
import os
import sys
import traceback
from math import copysign
from time import sleep, time

from .livecode import LiveExecution
from shoebot.core.events import (
    event_is,
    next_event,
    QUIT_EVENT,
    SET_WINDOW_TITLE_EVENT,
    SOURCE_CHANGED_EVENT,
    VARIABLE_CHANGED_EVENT,
    REDRAW_EVENT,
)
from shoebot.core.var_listener import VarListener
from shoebot.data import Variable
from shoebot.grammar.format_traceback import simple_traceback
from shoebot.util import UnbufferedFile

sys.stdout = UnbufferedFile(sys.stdout)
sys.stderr = UnbufferedFile(sys.stderr)

# If a bot is not animated the GUI is updated at 30fps
DEFAULT_GUI_UPDATE_SPEED = 30.0
DEFAULT_ANIMATION_SPEED = 60.0


class Grammar(object):
    """
    A Bot is an interface to receive user commands (through scripts or direct
    calls) and pass them to a canvas for drawing.

    Bae class for all Grammars, contains just the machinery for running the
    grammars, it has only the private API and nothing else, except for
    run which is called to actually run the Bot.
    """

    def __init__(self, canvas, namespace=None, vars=None):
        self._canvas = canvas
        self._dynamic = True  ##
        self._speed = None
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
                mouse_pointer_moved=self._mouse_pointer_moved,
            )
        self._input_device = input_device

    def _update_animation_variables(self, frame):
        # Update bot variables that change on each animation frame.
        self._namespace["FRAME"] = frame
        self._namespace["PAGENUM"] = frame

    def _load_namespace(self, namespace, filename=None):
        """
        Initialise bot namespace with info in shoebot.data

        :param filename: Will be set to __file__ in the namespace
        """
        from shoebot import data

        for name in dir(data):
            namespace[name] = getattr(data, name)

        for name in dir(self):
            if name[0] != "_":
                namespace[name] = getattr(self, name)

        namespace["_ctx"] = self  # Used in older nodebox scripts.
        namespace["__file__"] = filename

    #### Execute a single frame

    def _should_run(self, iteration, max_iterations):
        """ Return False if bot should quit """
        if iteration == 0:
            # First frame always runs.
            return True
        if max_iterations:
            # Run if this isn't the last frame.
            return iteration < max_iterations
        elif max_iterations is None:
            # Run forever if this isan animation, otherwise stop.
            return self._dynamic

        # Time to stop running.
        return False

    def _calculate_frame_delay(self, speed, start_time):
        """
        :return in seconds time to delay, taking into account execution time
        """
        if not speed:
            return 0

        # If the amount of time taken is more than the FPS delay
        # then return zero.
        return max((1.0 / abs(speed)) - (time() - start_time), 0.0)

    def run(
        self,
        inputcode,
        max_iterations=None,
        run_forever=False,
        frame_limiter=False,
        verbose=False,
    ):
        if os.path.isfile(inputcode):
            source = open(inputcode).read()
            filename = inputcode
        elif isinstance(inputcode, str):
            filename = "<string>"
            source = inputcode
        else:
            raise ValueError("inputcode must be a str or file like object.")

        self._load_namespace(self._namespace, filename)
        # TODO:  The shell module (sbio) accesses the executor via its name here,
        # making this event based would remove the need for this.
        self._executor = executor = LiveExecution(
            source, ns=self._namespace, filename=filename
        )

        if run_forever is False:
            if max_iterations is None:
                max_iterations = 1

        try:
            # Iterations only increment, whereas FRAME can decrement if the user sets a negative speed.
            iterations = 0
            first_run = True
            while first_run or iterations != max_iterations:
                # Main loop:
                # - Setup bot on first run.
                # - Run draw function for if present.
                # - Process events
                # - Update state
                start_time = time()
                iterations += 1

                canvas_dirty = False
                # Reset output graphics state
                self._canvas.reset_canvas()

                with executor.run_context() as (known_good, source, ns):
                    if not known_good:
                        # New code has been loaded, but it may have errors.
                        # Setting first_run forces the global context to be re-run
                        # Which has the side effect of loading all functions and state.
                        first_run = True

                    if first_run:
                        # Run code in the global namespace, followed by setup()
                        executor.run()
                        if "setup" in executor.ns:
                            executor.ns["setup"]()

                        # Store initial state so script can revert to a known state when livecoding.
                        self._initial_namespace = copy.copy(self._namespace)
                        canvas_dirty = True

                    is_animation = "draw" in executor.ns
                    if is_animation and self._speed != 0:
                        # If speed is 0, then don't output anything..
                        executor.ns["draw"]()
                        canvas_dirty = True

                if canvas_dirty:
                    self._canvas.flush(self._frame)

                if frame_limiter:
                    # Frame limiting is only used when running the GUI.
                    if is_animation:
                        # User specifies framerate, via speed(...) or use a default.
                        fps = self._speed
                        timeout = self._calculate_frame_delay(
                            fps if fps is not None else DEFAULT_ANIMATION_SPEED,
                            start_time,
                        )
                        next_frame_due = time() + timeout
                    else:
                        # Re-run the mainloop at 30fps, so that the GUI remains responsive.
                        next_frame_due = time() + 1.0 / DEFAULT_GUI_UPDATE_SPEED
                else:
                    # Do not sleep between frames.
                    next_frame_due = time()

                # Handle events
                continue_running, first_run = self._handle_events(
                    is_animation, next_frame_due
                )
                if not continue_running:
                    # Event handler returns False if it receives a message to quit.
                    break

            # Main loop has finished, return True to indicate it exited normally.
            return True
        except Exception as e:
            # Catch Exception, not BaseException, so that KeyboardInterrupts (ctrl+c) still work.
            # if something goes wrong, print verbose system output.

            import sys

            if verbose:
                errmsg = traceback.format_exc()
            else:
                errmsg = simple_traceback(e, executor.known_good or "")
            sys.stderr.write(f"{errmsg}\n")
            return False

    def _handle_events(self, is_animation, next_frame_due):
        """
        The Shoebot mainloop, GUI and shell communicate with each other using events.

        Examples include live variables being changed from the GUI, the shell
        or Shoebot itself, or the user quitting from the GUI.

        This handler waits for events and updates where needed, the loop also
        serves handles the delay between frames for animated bots.

        return: continue_running, restart
        """

        # Things we might want to do on returning:
        # Restart (if state has changed and not an animation).
        # Quit
        # Continue running.

        restart_bot = False
        while True:
            timeout = min(next_frame_due - time(), 0.1)
            event = next_event(
                block=timeout > 0, timeout=timeout if timeout > 0 else None
            )
            # Update GUI, which may in-turn generate new events.
            self._canvas.sink.main_iteration()

            if event is not None:
                if event.type == QUIT_EVENT:
                    # The user chose to quit via the shell or GUI.
                    return False, False
                elif event.type == REDRAW_EVENT:
                    # The GUI needs redrawing (usually because the Window was resized)
                    # TODO: This is a hack/workaround, since the graphics backend doesn't currently support redrawing
                    if not is_animation:
                        return True, True
                elif event.type == SET_WINDOW_TITLE_EVENT:
                    # A new window title was specified in the shell
                    self._canvas.sink.set_title(event.data)
                elif event.type == SOURCE_CHANGED_EVENT:
                    # New source code was loaded from the shell.
                    # Debounce SOURCE_CHANGED events -
                    # Gedit generates two events for changing a single character -
                    # delete and then add
                    while event and event.type == SOURCE_CHANGED_EVENT:
                        # TODO, can this be handled differently (non-blocking or just ignore source that is the same?)
                        event = next_event(block=True, timeout=0.001)
                    if not is_animation:
                        return True, True
                elif event.type == VARIABLE_CHANGED_EVENT:
                    # A Variable was changed, from the shell or the GUI.
                    # TODO, make VARIABLE_ADDED_EVENT, VARIABLE_DELETED_EVENT
                    # TODO, sketched out, fix up properly.
                    self._executor.ns[event.data.name] = event.data.value
                    # TODO: State was updated, bot needs to execute again ???
                    if not is_animation:
                        # On non-animated bots, updating variables re-runs the whole
                        # whole bot so that the user may see the updated state.
                        return True, True

            if time() >= next_frame_due:
                break

        if event is None:
            # event is None indicates the handler timed out.
            # If the bot is animated, then the next frame is due and
            # variables that update per-frame must be updated.

            if is_animation and self._speed is not None:
                if self._speed > 0:
                    self._frame += 1
                elif self._speed < 0:
                    self._frame -= 1
            self._update_animation_variables(self._frame)

        # By default return continue_running=True.
        return True, restart_bot

    def finish(self):
        ## For use when using shoebot as a module
        ## TODO: Not used when running as a bot, possibly should not be available in
        ## this case
        self._canvas.flush(self._frame)

    #### Variables
    def _addvar(self, v):
        """Sets a new accessible variable.

        :param v: Variable.
        """
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
