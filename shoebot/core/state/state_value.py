class StateValueContainer:
    def __init__(self, attribute_name: str, value = None):
        self.__state_attribute_name__ = attribute_name
        if value is not None:
            setattr(self, self.__state_attribute_name__, value)
    @property
    def __state_value__(self):
        return getattr(self, self.__state_attribute_name__)


def get_state_value(container: StateValueContainer):
    return container.__state_value__

def set_state_value(container: StateValueContainer, value):
    setattr(container, container.__state_attribute_name__, value)


class ReadWriteStateValueDescriptor:
    """
    Classes may be backed by an object that will be stored in a State object later on.
    """
    def __init__(self, state_container_type, field_name=None):
        self.state_container_type = state_container_type
        self.field_name = field_name

    def __set_name__(self, owner, name):
        print("__set_name__", owner, name, self.field_name, self.state_container_type)
        owner._state_container_fields[name] = self.state_container_type
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
        state_value = self.state_container_type(*value).__state_value__

        setattr(obj.__state__, self.field_name, state_value)
        obj.__state_values__[self.field_name] = state_value

