# Shoebot events
#
# Using python pubsub
#
# Currently VERY simple, just passing when to QUIT and RELOAD_SOURCE
#
# In future a lot of the could probably be simplified by using more events
# and less flags etc.

import pubsub

channel = pubsub.subscribe("shoebot")

QUIT_EVENT = "quit"
SOURCE_CHANGED_EVENT = "source-changed"
EVENT_VARIABLE_UPDATED = "variable-updated"


def next_event(timeout=None):
    try:
        return channel.listen(block=False, timeout=timeout).next()['data']
    except StopIteration:
        return
