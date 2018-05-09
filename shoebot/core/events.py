"""
The pubsub library enables communication between the GUI parts of shoebot
and the commandline shell.
"""

import collections
import pubsub

# Only the 'shoebot' channel is used
channel = pubsub.subscribe("shoebot")


def namedtuple_with_defaults(typename, field_names, default_values=()):
    T = collections.namedtuple(typename, field_names)
    T.__new__.__defaults__ = (None,) * len(T._fields)
    if isinstance(default_values, collections.Mapping):
        prototype = T(**default_values)
    else:
        prototype = T(*default_values)
    T.__new__.__defaults__ = tuple(prototype)
    return T


Event = namedtuple = namedtuple_with_defaults("Event", "type data", dict(data=None))

QUIT_EVENT = "quit"
SOURCE_CHANGED_EVENT = "source-changed"
VARIABLE_UPDATED_EVENT = "variable-updated"
SET_WINDOW_TITLE = "set-window-title"


def next_event(block=False, timeout=None):
    """
    Get the next available event or None

    :param block:
    :param timeout:
    :return: None or (event, data)
    """
    try:
        return channel.listen(block=block, timeout=timeout).next()['data']
    except StopIteration:
        return None


def event_is(event, event_t):
    """
    Check if event type
    :param event:   event to compare
    :param event_t: event type
    :return: bool
    """
    return event is not None and event.type == event_t


def publish_event(event_t, data=None, extra_channels=None, wait=None):
    """
    Publish an event ot any subscribers.

    :param event_t:  event type
    :param data:     event data
    :param extra_channels:
    :param wait:
    :return:
    """
    event = Event(event_t, data)
    pubsub.publish("shoebot", event)
    for channel_name in extra_channels or []:
        pubsub.publish(channel_name, event)
    if wait is not None:
        channel = pubsub.subscribe(wait)
        channel.listen(wait)
