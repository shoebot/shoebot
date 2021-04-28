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
)
from shoebot.core.var_listener import VarListener
from shoebot.data import Variable
from shoebot.grammar.format_traceback import simple_traceback
from shoebot.util import UnbufferedFile

sys.stdout = UnbufferedFile(sys.stdout)
sys.stderr = UnbufferedFile(sys.stderr)


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

    def run(self,
            inputcode,
            max_iterations=None,
            run_forever=False,
            frame_limiter=False,
            verbose=False):

        source = None
        filename = None

        if os.path.isfile(inputcode):
            source = open(inputcode).read()
            filename = inputcode
        elif isinstance(inputcode, str):
            filename = "<string>"
            source = inputcode

        self._load_namespace(self._namespace, filename)
        # self._executor is set so sbio can access it.
        self._executor = executor = LiveExecution(
            source, ns=self._namespace, filename=filename
        )

        if not max_iterations:
            if run_forever:
                max_iterations = None
            else:
                max_iterations = 1

        frame = None

        # main loop structure
        #
        # Run bot
        # Process events
        # Update state

        # Main loop
        while frame is None or frame != max_iterations and run_forever:
            start_time = time()
            # Run bot
            # TODO
            # First frame

            # Reset output graphics state
            self._canvas.reset_canvas()

            if frame is None:
                executor.run()
                if "setup" in executor.ns:
                    executor.ns["setup"]()

                if "draw" not in executor.ns:
                    self._canvas.flush(frame)
                frame = 0

            # Store initial state so script can revert to a known state when livecoding.
            self._initial_namespace = copy.copy(
                self._namespace
            )

            if "draw" in executor.ns and self._speed != 0:
                # If speed is 0, then the bot is paused.
                executor.ns["draw"]()
                self._canvas.flush(frame)

            fps = self._speed  # (speed may have been changed from within bot)

            is_animation = "draw" in executor.ns
            if frame_limiter:
                # Frame limiting is only used when running the GUI.
                if is_animation:
                    timeout = self._calculate_frame_delay(fps if fps is not None else 60, start_time)
                    next_frame_due = time() + timeout
                else:
                    next_frame_due = time() + (1.0 / 30)
            else:
                next_frame_due = time()

            # Handle events
            if not self._handle_events(is_animation, next_frame_due):
                # Event handler returns False if it receives a message to quit.
                break

            frame = self._frame  # TODO ?

    def _handle_events(self, is_animation, next_frame_due):
        """
        The Shoebot mainloop, GUI and shell communicate with each other using events.

        Examples include live variables being changed from the GUI, the shell
        or Shoebot itself, or the user quitting from the GUI.

        This handler waits for events and updates where needed, the loop also
        serves handles the delay between frames for animated bots.
        """

        # Things we might want to do on returning:
        # Restart (if state has changed and not an animation).
        # Quit
        # Continue running.

        while True:
            timeout = min(next_frame_due - time(), 0.01)
            event = next_event(block=timeout > 0, timeout=timeout if timeout > 0 else None)
            # Update GUI, which may in-turn generate new events.
            self._canvas.sink.main_iteration()

            if event is not None:
                if event.type == QUIT_EVENT:
                    return False
                elif event.type == SOURCE_CHANGED_EVENT:
                    # Debounce SOURCE_CHANGED events -
                    # Gedit generates two events for changing a single character -
                    # delete and then add
                    while event and event.type == SOURCE_CHANGED_EVENT:
                        # TODO, can this be handled differently (non-blocking or just ignore source that is the same?)
                        event = next_event(block=True, timeout=0.001)
                elif event.type == VARIABLE_CHANGED_EVENT:
                    # TODO, make VARIABLE_ADDED_EVENT, VARIABLE_DELETED_EVENT
                    # TODO, sketched out, fix up properly.
                    self._executor.ns[event.data.name] = event.data.value
                    # TODO: State was updated, bot needs to execute again ???
                    if not is_animation:
                        # On non-animated bots, updating variables re-runs the whole
                        # whole bot so that the user may see the updated state.
                        self._executor.run()
                        self._canvas.flush(self._frame)
                elif event.type == SET_WINDOW_TITLE_EVENT:
                    self._canvas.sink.set_title(event.data)

            if time() >= next_frame_due:
                break

        if event is None:
            # event == None, means the handler timed out.
            # If the bot is animated, then the next frame is due and
            # variables that update per-frame need to be updated.

            if is_animation and self._speed is not None:
                if self._speed > 0:
                    self._frame += 1
                elif self._speed < 0:
                    self._frame -= 1
            self._update_animation_variables(self._frame)

        # By default return True signalling to the main loop to carry on running.
        return True

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
