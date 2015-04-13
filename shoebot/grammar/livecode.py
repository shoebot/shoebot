import ast
import copy
import contextlib
import compiler.ast
import inspect
import meta.decompiler

class LiveExecution(object):
    """
    Live Code executor.

    Code has two states, 'known good' and 'tenous'
    
    "known good" can have exceptions and die
    "tenous code" exceptions attempt to revert to "known good"
    """
    ns = {}

    def __init__(self, source, ns=None, filename=None):
        self.edited_source = None
        self.known_good = source
        self.filename = filename
        if ns is None:
            self.ns = {}
        else:
            self.ns = ns

    def load_edited_source(self, source):
        """
        Load changed code into the execution environment.

        Until the code is executed correctly, it will be
        in the 'tenuous' state.
        """
        self.edited_source = source

    def reload_functions(self):
        """
        Recompile functions
        """
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
        ns_snapshot = copy.copy(self.ns)
        try:
            source = self.edited_source
            self.edited_source = None
            self.do_exec(source, ns_snapshot, True)
            self.known_good = source
            return True, None
        except Exception as e:
            self.ns.clear()
            self.ns.update(ns_snapshot)
            return False, e

    def run(self):
        """
        Attempt to known good or tenuous source.
        """
        if self.edited_source:
            success, ex = self.run_tenuous()
            if success:
                return

        self.do_exec(self.known_good, self.ns)

    @contextlib.contextmanager
    def run_context(self):
        """
        Context in which the user can run the source in a custom manner.

        If no exceptions occur then the source will move from 'tenuous'
        to 'known good'.

        >>> with run_context() as (tenuous, source, ns):
        >>> ...  exec source in ns
        >>> ...  ns['draw']()

        """
        if self.edited_source is None:
            yield True, self.known_good, self.ns
            return

        ns_snapshot = copy.copy(self.ns)
        try:
            yield False, self.edited_source, self.ns
            self.known_good = self.edited_source
            self.edited_source = None
        except Exception as e:
            self.edited_source = None
            self.ns.clear()
            self.ns.update(ns_snapshot)

