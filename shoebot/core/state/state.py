"""
Graphics state, such as the colour and size of of objects is
delegated to a dataclass in a __state__ attribute.

This separates the more complex APIs the users use from a simpler
intermediate representation that Renderers can use.

The state holds only the information needed by the Renderer, unlike
the Grobs which may have all sorts of extra APIs and methods.
"""

import abc
from dataclasses import fields
from typing import Type


class ReadOnlyDescriptor:
    def __init__(self, field_name=None):
        self.field_name = field_name

    def __set_name__(self, owner, name):
        if self.field_name is None:
            self.field_name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj.__state__, self.field_name)


class ReadWriteDescriptor:
    def __init__(self, field_name=None, writer=None):
        """
        field_name: the name of the field in the state object
        writer: a function that will be called on the value before it is set.
        """
        self.field_name = field_name
        self.writer = writer

    def __set_name__(self, owner, name):
        if self.field_name is None:
            self.field_name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj.__state__, self.field_name)

    def __set__(self, obj, value):
        if self.writer is not None:
            setattr(obj.__state__, self.field_name, self.writer(value))
        else:
            setattr(obj.__state__, self.field_name, value)


class ReadWriteStateValueDescriptor:
    """
    Classes may be backed by an object that will be stored in a State object later on.
    """
    def __init__(self, state_value_type, field_name=None):
        self.state_value_type = state_value_type
        self.field_name = field_name

    def __set_name__(self, owner, name):
        if self.field_name is None:
            self.field_name = name

    @staticmethod
    def ensure_state_storage(obj):
        """
        Ensure that the object has a ___state___values__ attribute to store state values in.
        """
        if not hasattr(obj, '__state_values__'):
            obj.__state_values__ = {}

    def __get__(self, obj, objtype=None):
        """
        Get the value of the state value stored in the ___state___values__ attribute.
        """
        if obj is None:
            return self
        self.ensure_state_storage(obj)
        return obj.__state_values__.get(self.field_name, None)

    def __set__(self, obj, value):
        """
        Set the value of the state value, and store the original value in the
        __state_values__ attribute.
        """
        self.ensure_state_storage(obj)
        state_value = self.state_value_type(value).__state_value__
        setattr(obj.__state__, self.field_name, state_value)
        obj.__state_values__[self.field_name] = value


    def __set__(self, obj, value):
        state_value = self.state_value_type(value).__state_value__
        setattr(obj.__state__, self.field_name, state_value)
        self.value = value

class State(metaclass=abc.ABCMeta):
    """
    In Shoebot Stateful objects such as Grobs delegate state storage to
    dataclasses that extend the State class in their __state__ attribute.

    Fields in the State dataclasses contain information needed by the Renderer
    to draw the object, such as the colour and size of the object.

    State provides utility methods to populate the dataclass during __init__,


    State provide from_kwargs() to populate the dataclass during __init__,
    and readonly_property() and readwrite_property() to create a properties that delegate to the
    dataclass.
    """
    @classmethod
    def from_kwargs(cls, __state__=None, **kwargs):
        """
        Create an instance of the dataclass using provided keyword arguments.

        Only includes arguments that match the names of fields in the dataclass.

        Extra arguments are omitted.

        :param __state__: An instance of the dataclass
        :param kwargs: Arbitrary keyword arguments.
        :return: An instance of the dataclass.
        """
        if __state__ is not None:
            return __state__
        
        # Create a set of field names for efficient lookup
        field_names = {field.name for field in fields(cls)}

        # Filter kwargs to include only keys that are valid field names
        valid_kwargs = {k: v for k, v in kwargs.items() if k in field_names}

        return cls(**valid_kwargs)

    @classmethod
    def readwrite_property(cls, field_name=None, writer=None):
        return ReadWriteDescriptor(field_name, writer=writer)

    @classmethod
    def readonly_property(cls, field_name=None):
        return ReadOnlyDescriptor(field_name)

    @classmethod
    def readwrite_state_value_property(self, stateful_type, field_name=None):
        """
        Create a property that is a stateful object itself.
        """
        # state_ref = StateRef(stateful_type)

        return ReadWriteStateValueDescriptor(stateful_type, field_name)