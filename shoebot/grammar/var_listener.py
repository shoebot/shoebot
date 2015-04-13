from contextlib import contextmanager


class VarListener(object):
    """
    Var listeners are used to notify things like
    the gui or socketserver when variables change
    """

    active = True # set to False to temporarily disable

    def __init__(self, listener):
        self.listener = listener

    def var_added(self, v):
        if VarListener.active:
            self.listener.var_added(v)

    def vars_added(self, vs):
        for v in vs:
            self.var_added(v)

    def var_deleted(self, v):
        if VarListener.active:
            self.listener.var_deleted(v)
        else:
            print('VarListener not active')

    def vars_deleted(self, vs):
        print('>>> vars_deleted')
        for v in vs:
            self.var_deleted(v)

    def var_updated(self, v):
        if VarListener.active:
            self.listener.var_updated(v)

    def vars_updated(self, vs):
        for v in vs:
            self.var_updated(v)

    @staticmethod
    @contextmanager
    def disabled():
        """
        Context manager to temporarily disable all listeners

        >>> with VarListener.disabled()
        ...     pass
        """
        VarListener.active = False
        yield
        VarListener.active = True

    @staticmethod
    @contextmanager
    def batch(vars, oldvars, listeners=None):
        """
        Context manager to only update listeners
        at the end, in the meantime it doesn't
        matter what intermediate state the vars
        are in (they can be added and removed)

        >>> with VarListener.batch()
        ...     pass
        """
        snapshot_vars = dict(vars)

        with VarListener.disabled():
            yield

        added_vars = set(oldvars.keys()) - set(snapshot_vars.keys())
        deleted_vars = set(snapshot_vars.keys()) - set(oldvars.keys())
        for listener in listeners or []:
            for name in added_vars:
                listener.var_added(vars[name])
            for name in deleted_vars:
                listener.var_deleted(snapshot_vars[name])
