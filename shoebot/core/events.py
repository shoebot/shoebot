"""The pubsub library enables communication between the GUI parts of shoebot
and the commandline shell."""

import collections
import queue

from pubsub import pub


def namedtuple_with_defaults(typename, field_names, default_values=()):
    T = collections.namedtuple(typename, field_names)
    T.__new__.__defaults__ = (None,) * len(T._fields)
    if isinstance(default_values, collections.abc.Mapping):
        prototype = T(**default_values)
    else:
        prototype = T(*default_values)
    T.__new__.__defaults__ = tuple(prototype)
    return T


Event = namedtuple = namedtuple_with_defaults("Event", "type data", dict(data=None))

QUIT_EVENT = "quit"
SOURCE_CHANGED_EVENT = "source-changed"
VARIABLE_CHANGED_EVENT = "variable-updated"
SET_WINDOW_TITLE_EVENT = "set-window-title"
REDRAW_EVENT = "redraw"

def publish_event(event_t, data=None, **kwargs):
    """Publish an event ot any subscribers.

    :param event_t:  event type
    :param data:     event data
    :param extra_channels:
    :param wait:
    :return:
    """
    event = Event(event_t, data, **kwargs)
    pub.sendMessage('shoebot', event=event, **kwargs)


def route_events_to_queue(event_queue: queue.Queue, channel:str):
    """
    Adapter to route pubsub events for a particular channel to a queue.
    """
    def add_incoming_event_to_queue(event=None):
        """Shoebot uses a pub/sub architecture to communicate between the
        different components such as the bot, GUI and command interface.

        This function is called when a message is received, it is
        put on a queue.
        """
        event_queue.put_nowait(event)

    pub.subscribe(add_incoming_event_to_queue, channel)
