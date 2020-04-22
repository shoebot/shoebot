"""
Check if shoebot can create files in it's supported output formats
and that none are zero bytes long.
"""
import tempfile
import textwrap
import unittest

from parameterized import parameterized, parameterized_class

from tests.unittests.helpers import (
    ShoebotTestCase,
)


class TestTraceback(ShoebotTestCase):
    def test_output_formats(self):
        """
        Run a simple bot for each supported output format and verify the output.
        """
        code = textwrap.dedent("""\
        background(0)
        raise Exception()
        """)
        with tempfile.NamedTemporaryFile(suffix=f".png") as f:
            self.run_code(code, outputfile=f.name, windowed=False)


if __name__ == "__main__":
    unittest.main(buffer=True)
