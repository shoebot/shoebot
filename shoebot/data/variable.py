NUMBER = 1
TEXT = 2
BOOLEAN = 3
BUTTON = 4

DEFAULT_STEPS = 256.0


def clamp(minvalue, value, maxvalue):
    return max(minvalue, min(value, maxvalue))


class Variable(object):
    """Taken from Nodebox"""

    def __init__(self, name, type, **kwargs):
        """Creates a live variable, which can be manipulated using the
        variables UI, socket server or live coding shell.

        :param name: variable name
        :param type: variable type
        :type type: NUMBER, TEXT, BOOLEAN or BUTTON
        :param default: default value
        :param min: minimum value (NUMBER only)
        :param max: maximum value (NUMBER only)
        :param value: initial value (if not defined, use ``default``)
        :param step: step length for the variables GUI (use this or ``steps``, not both)
        :param steps: number of steps in the variables GUI (use this or ``step``, not both)
        """
        self.name = name
        if not isinstance(name, str):
            raise AttributeError("Variable name must be a string")
        if kwargs.get("step") and kwargs.get("steps"):
            raise AttributeError(
                "Can only set step or steps"
            )  # TODO - is this too strict
        self.type = type or NUMBER
        self.min = None
        self.max = None
        self.step = None or kwargs.get("step")
        self.steps = kwargs.get("steps", DEFAULT_STEPS)
        if self.type == NUMBER:
            self.min = kwargs.get("min", 0.0)
            self.max = kwargs.get("max", 100.0)
            if self.step is None:
                diff = max(self.min, self.max) - min(self.min, self.max)
                self.step = diff / float(self.steps)
            self.default = kwargs.get("default")
            if self.default is None:
                self.default = self.min
        elif self.type == TEXT:
            self.default = kwargs.get("default", "bonjour")
        elif self.type == BOOLEAN:
            self.default = kwargs.get("default", True)
        elif self.type == BUTTON:
            self.default = kwargs.get("default", self.name)
        else:
            raise AttributeError(
                "Variables must be of type NUMBER, TEXT, BOOLEAN or BUTTON"
            )
        self.value = kwargs.get("value", self.default)
        if self.value is None and self.default is not None:
            self.value = self.default

    def sanitize(self, val):
        """Given a Variable and a value, cleans it out"""
        if self.type == NUMBER:
            try:
                return clamp(self.min, self.max, float(val))
            except ValueError:
                return 0.0
        elif self.type == TEXT:
            try:
                return str(str(val), "utf_8", "replace")
            except:
                return ""
        elif self.type == BOOLEAN:
            if str(val).lower() in ("true", "1", "yes"):
                return True
            else:
                return False

    def compliesTo(self, v):
        """Return whether I am compatible with the given var:
        - Type should be the same
        - My value should be inside the given vars' min/max range.
        """
        if self.type == v.type:
            if self.type == NUMBER:
                if self.value < self.min or self.value > self.max:
                    return False
            return True
        return False

    def __repr__(self):
        return "Variable(name=%s, type=%s, default=%s, min=%s, max=%s, value=%s)" % (
            self.name,
            self.type,
            self.default,
            self.min,
            self.max,
            self.value,
        )
