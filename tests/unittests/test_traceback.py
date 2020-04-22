"""
Check if shoebot can create files in it's supported output formats
and that none are zero bytes long.
"""
import contextlib
import io
import tempfile
import textwrap
import unittest

from parameterized import parameterized, parameterized_class

from tests.unittests.helpers import ShoebotTestCase


class TestSimpleTraceback(ShoebotTestCase):
    def test_simple_traceback(self):
        """
        Check the simplified traceback has the expected content
        by redirecting sterr while a script runs that generates
        an exception.
        """
        code = textwrap.dedent(
            """\
        background(0)
        raise Exception("Oh no")
        """
        )
        expected_output = textwrap.dedent(
            """\
        Error in the Shoebot script at line 2:
        1: background(0)
        2: raise Exception("Oh no")
           ^ Exception: Oh no

        Traceback (most recent call last):
          File "<string>", line 2, in <module>
        Exception: Oh no
        """
        )

        with tempfile.NamedTemporaryFile(suffix=f".png") as f:
            output_buffer = io.StringIO()
            with contextlib.redirect_stderr(output_buffer):
                self.run_code(code, outputfile=f.name, windowed=False)
                actual_output = output = output_buffer.getvalue()

        self.assertEqual(actual_output, expected_output)


if __name__ == "__main__":
    unittest.main(buffer=False)
