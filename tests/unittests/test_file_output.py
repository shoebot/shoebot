"""
Check if shoebot can create files in it's supported output formats
and that none are zero bytes long.
"""
import tempfile
import unittest

from pathlib import Path
from parameterized import parameterized

from shoebot import create_bot

class TestOutputFormats(unittest.TestCase):

    def assertOutputFile(self, filename):
        """
        Verify file exists and is more than 0 bytes.
        """
        self.assertTrue(Path(filename).is_file(), f"{filename} does not exist")
        self.assertNotEqual(0, Path(filename).stat().st_size, f"{filename} is zero bytes")

    @parameterized.expand(["png", "ps", "pdf", "svg"])
    def test_output_formats(self, file_format):
        """
        Run a simple bot for each supported output format and verify the output.
        """
        with tempfile.NamedTemporaryFile(suffix=f".{file_format}") as f:
            bot = create_bot(outputfile=f.name)
            
            bot.run("background(0)")

            self.assertOutputFile(f.name)

if __name__ == '__main__':
    unittest.main()
