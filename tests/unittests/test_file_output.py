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

from .util import TestSequence

FORMATS = ["png", "ps", "pdf", "svg"]
BOT_CODE = "background(0)"

def run_shoebot_code(code, outputfile):
    bot = shoebot.create_bot(outputfile=outputfile)
    bot.run(code)
    return outputfile


def create_output_test(fmt):
    def test(self):
        h, fn = tempfile.mkstemp(suffix=".%s" % fmt)
        run_shoebot_code(BOT_CODE, outputfile=fn)
        self.assertTrue(exists(fn), "%s was not created" % fn)
        size_not_zero = stat(fn).st_size != 0
        self.assertTrue(size_not_zero, "%s is zero bytes." % fn)
        unlink(fn)
    return test


class TestFileOutput(unittest.TestCase):
    __metaclass__ = TestSequence

    test_create = ("test_create_%s", create_output_test, FORMATS)

if __name__ == '__main__':
    unittest.main()
