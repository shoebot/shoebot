"""
Graphics state, such as the colour and size of of objects is
delegated to a dataclass in a _state attribute.

This separates the more complex APIs the users use from a simpler
intermediate representation that Renderers can use.

The state holds only the information needed by the Renderer, unlike
the Grobs which may have all sorts of extra APIs and methods.
"""

import abc
from dataclasses import fields



class ReadOnlyDescriptor:
    def __init__(self, field_name=None):
        self.field_name = field_name

    def __set_name__(self, owner, name):
        if self.field_name is None:
            self.field_name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj._state, self.field_name)


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
        return getattr(obj._state, self.field_name)

    def __set__(self, obj, value):
        if self.writer is not None:
            setattr(obj._state, self.field_name, self.writer(value))
        else:
            setattr(obj._state, self.field_name, value)


# class ReadWriteSubDescriptor:
#     """
#     Sometimes a descriptor needs to be a stateful object itself,
#     for example fill and stroke colors of a BezierPath.
#
#     In those cases the state of the sub, in that case the state of the
#     color is owned by the BezierPath, not the Color.
#     """
#     def __init__(self, container_type=None, field_name=None, writer=None):
#         """
#         container_type: the type of the container that owns the state
#         field_name: the name of the field in the state object
#         writer: a function that will be called on the value before it is set.
#         """
#         self.container_type = container_type
#         self.field_name = field_name
#         self.writer = writer
#
#     def __set_name__(self, owner, name):
#         if self.field_name is None:
#             self.field_name = name
#
#     def __get__(self, obj, objtype=None):
#         if obj is None:
#             return self
#         return getattr(obj._state, self.field_name)
#
#     def __set__(self, obj, value):
#         if self.writer is not None:
#             setattr(obj._state, self.field_name, self.writer(value))
#         else:
#             setattr(obj._state, self.field_name, value)

class State(metaclass=abc.ABCMeta):
    """
    In Shoebot Stateful objects such as Grobs delegate state storage to
    dataclasses that extend the State class in their _state attribute.

    Fields in the State dataclasses contain information needed by the Renderer
    to draw the object, such as the colour and size of the object.

    State provides utility methods to populate the dataclass during __init__,


    State provide from_kwargs() to populate the dataclass during __init__,
    and readonly_property() and readwrite_property() to create a properties that delegate to the
    dataclass.
    """
    @classmethod
    def from_kwargs(cls, _state=None, **kwargs):
        """
        Create an instance of the dataclass using provided keyword arguments.

        Only includes arguments that match the names of fields in the dataclass.

        Extra arguments are omitted.

        :param _state: An instance of the dataclass
        :param kwargs: Arbitrary keyword arguments.
        :return: An instance of the dataclass.
        """
        if _state is not None:
            return _state
        
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

    # def readonly_subproperty(self, container_type=None, field_name=None, writer=None):
    #     if writer:
    #         raise NotImplementedError("writer not implemented for subproperty")
    #     return ReadOnlySubDescriptor(container_type, field_name)