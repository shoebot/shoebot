import _ast
import ast
import copy
import contextlib
import threading
import traceback


class LiveExecution(object):
    """
    Live Code executor.

    Code has two states, 'known good' and 'tenous'

    Known good:  Exceptions are raised as normal
    Tenuous: An exception will cause the code to be reverted to the last Known Good code

    Initially code is known-good, new code sent to the executor is tenuous, until
    it has been executed at least once.
    """

    ns = {}
    lock = threading.RLock()

    def __init__(self, source, ns=None, filename=None):
        self.edited_source = None
        self.known_good = source
        self.filename = filename
        if ns is None:
            self.ns = {}
        else:
            self.ns = ns

        self.good_cb = None
        self.bad_cb = None

    @property
    def is_edited(self):
        """
        :return: True if source has been edited
        """
        return self.edited_source is not None

    def load_edited_source(self, source, good_cb=None, bad_cb=None, filename=None):
        """
        Load changed code into the execution environment.

        Until the code is executed correctly, it will be
        in the 'tenuous' state.
        """
        with LiveExecution.lock:
            self.good_cb = good_cb
            self.bad_cb = bad_cb
            try:
                # Test compile (TODO - keep the binary object + use that)
                source = f"{source}\n\n"
                compile(source, filename or self.filename, "exec")
                self.edited_source = source
            except Exception as e:  # noqa
                if bad_cb:
                    self.edited_source = None
                    tb = traceback.format_exc()
                    self.call_bad_cb(tb)
                return
            if filename is not None:
                self.filename = filename

    def reload_functions(self, edited=True):
        """
        Reload functions, from edited_source or known_good

        :param edited: if True then functions are reloaded from edited_source, otherwise known_good is used.
        """
        if edited:
            source = self.edited_source
        else:
            source = self.known_good

        with LiveExecution.lock:
            if source is not None:
                compiled_modules = {}
                tree = ast.parse(source)
                for f in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
                    module = _ast.Module(body=[f], type_ignores=[])
                    code = compiled_modules.get(module)
                    if code is None:
                        code = compile(module, self.filename, "exec")
                        compiled_modules[module] = code

                    function_context = {}
                    eval(code, dict(self.ns), function_context)
                    self.ns[f.name].__code__ = function_context[f.name].__code__

    def do_exec(self, source, ns):
        """
        Override if you want to do something other than exec in ns

        tenuous is True if the source has just been edited and may fail
        """
        exec(source, ns)

    def run_tenuous(self):
        """
        Run edited source, if no exceptions occur then it
        graduates to known good.
        """
        with LiveExecution.lock:
            ns_snapshot = copy.copy(self.ns)
            try:
                source = self.edited_source
                self.edited_source = None
                self.do_exec(source, ns_snapshot)
                self.known_good = source
                self.call_good_cb()
                return True, None
            except Exception as ex:
                tb = traceback.format_exc()
                self.call_bad_cb(tb)
                self.ns.clear()
                self.ns.update(ns_snapshot)
                return False, ex

    def run(self):
        """
        Attempt to known good or tenuous source.
        """
        with LiveExecution.lock:
            if self.edited_source:
                success, ex = self.run_tenuous()
                if success:
                    return

            self.do_exec(self.known_good, self.ns)

    def clear_callbacks(self):
        """
        clear the good and bad callbacks
        """
        with LiveExecution.lock:
            self.bad_cb = None
            self.good_cb = None

    def call_bad_cb(self, tb):
        """
        If bad_cb returns True then keep it
        :param tb: traceback that caused exception
        :return:
        """
        with LiveExecution.lock:
            if self.bad_cb and not self.bad_cb(tb):
                self.bad_cb = None

    def call_good_cb(self):
        """
        If good_cb returns True then keep it
        :return:
        """
        with LiveExecution.lock:
            if self.good_cb and not self.good_cb():
                self.good_cb = None

    @contextlib.contextmanager
    def run_context(self):
        """
        Context in which the user can run the source in a custom manner.

        If no exceptions occur then the source will move from 'tenuous'
        to 'known good'.

        >>> with run_context() as (known_good, source, ns):
        >>> ...  exec source in ns
        >>> ...  ns['draw']()

        """
        with LiveExecution.lock:
            if self.edited_source is None:
                yield True, self.known_good, self.ns
                return

            ns_snapshot = copy.copy(self.ns)
            try:
                yield False, self.edited_source, self.ns
                self.known_good = self.edited_source
                self.edited_source = None
                self.call_good_cb()
                return
            except Exception as ex:
                tb = traceback.format_exc()
                self.call_bad_cb(tb)
                self.edited_source = None
                self.ns.clear()
                self.ns.update(ns_snapshot)
                self.reload_functions(edited=False)
