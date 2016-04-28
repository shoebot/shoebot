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


class TestFileOutput(unittest.TestCase):
    """
    Tests are added to this for all output formats.
    """
    pass

def create_output_tests(fmt, testName):
    def testCreateFile(self):
        test.__name__ = testName
        h, fn = tempfile.mkstemp(suffix=".%s" % fmt)
        run_shoebot_code(BOT_CODE, outputfile=fn)
        self.assertTrue(exists(fn), "%s was not created" % fn)
        size_not_zero = stat(fn).st_size != 0
        self.assertTrue(size_not_zero, "%s is zero bytes." % fn)
        unlink(fn)
    return testCreateFile

if __name__ == '__main__':
    for fmt in FORMATS:
        name = 'testCreate%s' % fmt.upper()
        test = create_output_tests(fmt, name)
        setattr(TestFileOutput, test.__name__, test)
    unittest.main()


if __name__ == '__main__':
    unittest.main()
