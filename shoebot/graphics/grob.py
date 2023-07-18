# TODO, Move 'bot' out of here, push responsibility back to 'Nodebox' and other grammars,
#       Enabling seperation of BezierPath etc

from shoebot.core.backend import cairo

# Alignments
CENTER = "center"
CORNER = "corner"
CORNERS = "corners"

# TODO - Move these to Context
STATES = {
    "transform": "_transform",
    "fillcolor": "_fillcolor",
    "fillrule": "_fillrule",
    "strokecolor": "_strokecolor",
    "strokewidth": "_strokewidth",
    "strokecap": "_strokecap",
    "strokejoin": "_strokejoin",
    "strokedash": "_strokedash",
    "dashoffset": "_dashoffset",
    "blendmode": "_blendmode",
    "align": "_align",
    "fontsize": "_fontsize",
    "lineheight": "_lineheight",
}


# class StateMeta(type):
#     """
#     Metaclass for Grob.
#
#     Checks for a ._state_attributes class attribute on the class and it's bases, and adds
#     a .state_attributes set to the class with the union of all of them.
#     """
#
#     def __new__(cls, name, bases, attrs):
#         state_attributes = set()
#         for base in bases:
#             if hasattr(base, "_state_attributes"):
#                 state_attributes.update(base._state_attributes)
#         if "_state_attributes" in attrs:
#             state_attributes.update(attrs["_state_attributes"])
#         attrs["state_attributes"] = state_attributes
#         # Map between the state attributes and the _underscored names used to store them.
#         attrs["state_attribute_names"] = {f"_{attr}": attr for attr in state_attributes}
#         return super().__new__(cls, name, bases, attrs)
#
#
# class StateMixin:
#     def __init__(self, **kwargs):
#         self._initialize_state(**kwargs)
#
# def _initialize_state(self, **kwargs):
#     """
#     Initializes the state attributes of the object (e.g. self._fillcolor) from the kwargs.
#     """
#     print("StateMixin._initialize_state")
#     for _name, name in self.state_attribute_names.items():
#         print(f"  >  {type(self).__name__}  {_name}={kwargs.get(name, None)}")
#         setattr(self, _name, kwargs.get(name, None))
#         print("  >>", getattr(self, _name))
#
# def frozen_state(self):
#     """
#     Returns a dict of the state attributes of the object.
#
#     Anything not set, falls back to the value in context.
#     """
#     # TODO - it might be more optimal to keep track of changes in the context (global and local)
#     # and then it may not be necessary to do this every draw call.
#     state = {}
#     for _name, name in self.state_attribute_names.items():
#         value = getattr(self, _name)
#         if value is None:
#             state[name] = getattr(self._context, _name)
#         else:
#             state[name] = value
#     return state


#class Grob(StateMixin, metaclass=StateMeta):
class Grob:

    """
    A GRaphic OBject is the base class for all DrawingPrimitives.

    Base classes should provide a _state_attributes class attribute.
    attributes named there will be added to an .state_attributes
    and automatically initialized in the constructor.
    """

    # _state_attributes = set()
    """Names of attributes that track drawing state."""

    def __init__(self, context, **kwargs):
        # Takes bot rather than canvas for compatibility with libraries - e.g. the colors library
        #StateMixin.__init__(self, **kwargs)
        canvas = context._canvas
        self._canvas = canvas
        self._context = context
        self._set_mode(canvas.mode)
        # TODO - _transform is currently cairo-ified...
        # self._transform = cairo.Matrix(*canvas.transform)
        self._transform = None  # TODO


    def _set_mode(self, mode):
        """Sets call_transform_mode to point to the center_transform or
        corner_transform."""
        if mode == CENTER:
            self._call_transform_mode = self._center_transform
        elif mode == CORNER:
            self._call_transform_mode = self._corner_transform
        else:
            raise ValueError("mode must be CENTER or CORNER")

    def _get_center(self):
        """Implementations must return the x, y of their center."""
        raise NotImplementedError()

    def _call_transform_mode(self):
        """This should never get called: set mode, changes the value of this to
        point.

        corner_transform or center_transform
        """
        raise NotImplementedError("_call_transform_mode called without mode set!")

    def _center_transform(self, transform):
        """Based on setupTransform from Java nodebox
        https://github.com/nodebox/nodebox/blob/master/src/main/java/nodebox/graphics/Grob.java."""
        # TODO: Port from cairo to Affine (or something else)
        dx, dy = self._get_center()
        t = cairo.Matrix()
        t.translate(dx, dy)
        t = transform * t
        t.translate(-dx, -dy)
        return t

    def _corner_transform(self, transform):
        """CORNER is the default, so we just return the transform."""
        return transform

    def inheritFromContext(self, ignore=()):
        """Doesn't store exactly the same items as Nodebox for ease of
        implementation, it has enough to get the Nodebox Dentrite example
        working."""
        for attr in type(self).state_attributes - set(ignore):  # no qa
            setattr(self, attr, getattr(self._context, attr))
