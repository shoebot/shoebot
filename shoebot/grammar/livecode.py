import ast
import copy
import contextlib
import threading
import traceback
import meta.decompiler


class LiveExecution(object):
    """
    Live Code executor.

    Code has two states, 'known good' and 'tenous'
    
    "known good" can have exceptions and die
    "tenous code" exceptions attempt to revert to "known good"
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
                # text compile
                compile(source + '\n\n', filename or self.filename, "exec")
            except Exception as e:
                if bad_cb:
                    self.edited_source = None
                    tb = traceback.format_exc()
                    self.call_bad_cb(tb)
                return
            if filename is not None:
                self.filename = filename
            self.edited_source = source

    def reload_functions(self):
        """
        Recompile functions
        """
        with LiveExecution.lock:
            if self.edited_source:
                source = self.edited_source
                tree = ast.parse(source)
                for f in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
                    # TODO - Could modify __code__ etc of functions, but this info will
                    # need to be saved if thats the case

                    self.ns[f.name] = meta.decompiler.compile_func(f, self.filename, self.ns)

    def do_exec(self, source, ns, tenuous = False):
        """
        Override if you want to do something other than exec in ns

        tenuous is True if the source has just been edited and may fail
        """
        exec source in ns

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
                self.do_exec(source, ns_snapshot, True)
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

