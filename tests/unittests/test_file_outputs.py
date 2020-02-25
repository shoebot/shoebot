"""
Check if shoebot can create files in it's supported output formats
and that none are zero bytes long.
"""
import tempfile
import unittest

from parameterized import parameterized, parameterized_class

from tests.unittests.helpers import ShoebotTestCase


@parameterized_class([{"windowed": False}, {"windowed": True}])
class TestOutputFormats(ShoebotTestCase):
    windowed = False  # False for headless, True for GUI

    @parameterized.expand(["png", "ps", "pdf", "svg"])
    def test_output_formats(self, file_format):
        """
        Run a simple bot for each supported output format and verify the output.
        """
        with tempfile.NamedTemporaryFile(suffix=f".{file_format}") as f:
            self.run_code("background(0)", outputfile=f.name, windowed=self.windowed)

            self.assertOutputFile(f.name)


if __name__ == "__main__":
    unittest.main(buffer=False)
