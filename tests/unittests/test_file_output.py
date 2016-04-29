"""
Check if shoebot can create files in all it's different output formats
and that none are zero bytes long.
"""

import tempfile
import unittest

from os import stat, unlink
from os.path import exists

import shoebot

from shoebot.core import CairoCanvas, CairoImageSink
from shoebot.data import BezierPath
from shoebot.grammar import NodeBot


FORMATS = ["png", "ps", "pdf", "svg"]
BOT_CODE = "background(0)"

def run_shoebot_code(code, outputfile):
    bot = shoebot.create_bot(outputfile=outputfile)
    bot.run(code)
    return outputfile


class TestFileOutputMeta(type):
    def __new__(mcs, name, bases, dct):
        def create_output_test(fmt, name):
            def test(self):
                h, fn = tempfile.mkstemp(suffix=".%s" % fmt)
                run_shoebot_code(BOT_CODE, outputfile=fn)
                self.assertTrue(exists(fn), "%s was not created" % fn)
                size_not_zero = stat(fn).st_size != 0
                self.assertTrue(size_not_zero, "%s is zero bytes." % fn)
                unlink(fn)
            return test

        for fmt in FORMATS:
            test_name = 'test_create_' + fmt
            dct[test_name] = create_output_test(fmt, name)
        
        return type.__new__(mcs, name, bases, dct)

class TestSequence(unittest.TestCase):
    __metaclass__ = TestFileOutputMeta

if __name__ == '__main__':
    unittest.main()
