import ast
import functools
import queue
import sys
import traceback
from pathlib import Path
from typing import Optional, Dict

from shoebot.core.canvas import Canvas
from shoebot.core.events import (
    SOURCE_CHANGED_EVENT,
    SET_WINDOW_TITLE_EVENT,
    REDRAW_EVENT,
    VARIABLE_CHANGED_EVENT,
    QUIT_EVENT,
    route_events_to_queue,
)
from shoebot.grammar.nodebox import NodeBotContext


# TODO:
# Port from shoebot/grammar/grammar.py:
# Event handling
# run method.


# Notes:
# In Nodebox "Context" it holds the Canvas and the namespace
# Shoebot has Nodebox->Bot->Grammar
#
# def __init__(self):
#     # Force NSApp initialisation.
#     NSApplication.sharedApplication().activateIgnoringOtherApps_(0)
#     self.namespace = {}
#     self.canvas = graphics.Canvas()
#     self.context = graphics.Context(self.canvas, self.namespace)
#     self.__doc__ = {}
#     self._pageNumber = 1
#     self.frame = 1
#
#
# Porting GUI event handling:
#   input_device is currently setup in Grammar
#   set_callbacks is used, this could be setup here
#
# Porting shoebot events:
# Move _even_queue from Grammar to here
# Consider porting GUI events to _event_queue

def context_as_dict(context, **overrides):
    """
    :param context: Shoebot Context.
    :return: dict of all public members.
    """
    # TODO - move this somewhere sane

    api = {
        name: getattr(context, name)
        for name in dir(context)
        if not name.startswith('_')
    }

    return {**api, **context._namespace, **overrides}

@functools.lru_cache(maxsize=2)
def is_animation(code):
    """
    :return True: if the code contains a draw function.

    Caches result for the last two code strings, which accounts
    for edited code and the previous code, which may need to
    be reverted to.
    """
    # Use AST to check if the code contains a 'draw' function
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'draw':
            return True
    return False

class ShoebotRunner:
    """
    The runner links "context" the users code runs in (e.g. the namespace),
    the output and does event handling.
    """

    def __init__(self, output, namespace: Optional[Dict] = None):
        """
        :param output: Output object to render to.
        :param namespace: Initial namespace.

        Output
        """
        assert output is not None, "Output must be provided."
        self.output = output
        self.canvas = Canvas(output)
        self.context = NodeBotContext(self.canvas, namespace)
        self.event_queue = queue.Queue()

        route_events_to_queue(self.event_queue, "shoebot")

    def run_once(self, code, extra_ns):
        """
        exec the passed in str or code object in the Shoebot namespace.
        """
        ns = context_as_dict(self.context, **extra_ns)

        # TODO - new_page may not be the right abstraction
        with self.canvas.new_page(self.context):
            exec(code, ns)

    def run_test_once(self, test_function, test_args, test_kwargs, extra_ns):
        """
        Variant of run_once that takes a function and adds the Shoebot API to
        it's namespace, for use in unit tests via shoebot_script_test decorator.
        """
        ns = context_as_dict(self.context, **extra_ns)
        with self.canvas.new_page(self.context):
            test_function.__globals__.update({**ns, **extra_ns})
            test_function(*test_args, **test_kwargs)

    def run(self, code):
        #  max_iterations=None, run_forever=False, frame_limiter=False, verbose=False):
        # TODO - port this from shoebot/grammar/bot.py
        # TODO - params

        # TODO: move this next block out of here to the caller.
        if Path(code).is_file():
            source = Path(code).read_text()
            filename = code
        elif isinstance(code, str):
            filename = "<string>"
            source = code
        else:
            raise ValueError("inputcode must be a str or file like object.")

        frame = 1
        iteration = 1
        while True:
            source_changed = False

            while self.event_queue.qsize() > 0:
                event = self.event_queue.get_nowait()
                if event.type == QUIT_EVENT:
                    return
                elif event.type == SOURCE_CHANGED_EVENT:
                    # New source code supplied
                    source = event.data
                    filename = event.filename
                    source_changed = True
                    # TODO - we need a way to send an event back about whether
                    # the an exception occurred and associate it with the correct
                    # source code
                elif event.type == VARIABLE_CHANGED_EVENT:
                    raise NotImplementedError("VARIABLE_CHANGED_EVENT")
                elif event.type == SET_WINDOW_TITLE_EVENT:
                    raise NotImplementedError("SET_WINDOW_TITLE_EVENT")
                elif event.type == REDRAW_EVENT:
                    raise NotImplementedError("REDRAW_EVENT")
                    # TODO
                else:
                    raise ValueError(f"Unknown event type {event.type}")

            try:
                # TODO - handling extra_ns should probably be somewhere else,
                #        (here should be grammar neutral)
                self.run_once(source,
                              extra_ns={"FRAME": frame,
                                        "ITERATION": iteration,
                                        "PAGE_NUM": frame,
                                        }
                              )
            except RuntimeError:
                if source_changed:
                    # TODO: send event back to interested parties containing
                    # the exception
                    pass
                print(traceback.format_exc(), file=sys.stderr)
                raise
            else:
                # TODO frame handling should be somewhere grammar neutral.
                iteration += 1
                frame += 1
                if source_changed:
                    # TODO: send event indicating successful run back to interested parties.
                    pass

            # TODO - sort out exactly destroy_renderer is called.
            if not hasattr(self.output, "renderer"):
                print("Create renderer with default size")
                # TODO - do this somewhere appropriate.
                self.output.create_renderer(400, 400)
            self.output.renderer.render_canvas(self.canvas)
            self.output.destroy_renderer()
            return # TODO - for now exit after 1 frame
            ## self.canvas.display()  # TODO - just for prototyping.
            ## await asyncio.sleep(.5)  # TODO let bot set speed
