"""Check if shoebot can create files in it's supported output formats and that
none are zero bytes long."""
import contextlib
import io
import tempfile
import textwrap
import unittest

from tests.unittests.helpers import ShoebotTestCase


class TestSimpleTraceback(ShoebotTestCase):
    # If traceback output changes then these tests will need to be updated.
    def test_simple_traceback_from_string(self):
        """Check the simplified traceback has the expected content by
        redirecting sterr while a script runs that generates an exception."""
        code = textwrap.dedent(
            """\
        background(0)
        raise Exception("Oh no")
        """,
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
        """,
        )

        with tempfile.NamedTemporaryFile(suffix=f".png") as f:
            output_buffer = io.StringIO()
            with contextlib.redirect_stderr(output_buffer):
                self.run_code(code, outputfile=f.name, windowed=False, verbose=False)
                actual_output = output_buffer.getvalue()

        self.assertEqual(actual_output, expected_output)

    def test_simple_traceback_from_bot_file(self):
        """Check the simplified traceback has the expected content by
        redirecting sterr while a bot file that generates an exception."""
        expected_output = textwrap.dedent(
            """\
        Error in the Shoebot script at line 4:
        1: # Raise Exception so the traceback formatting can be tested.
        2: #
        3: background(1, 1, 0)
        4: raise Exception("Oh dear.")
           ^ Exception: Oh dear.

        Traceback (most recent call last):
          File "<string>", line 4, in <module>
        Exception: Oh dear.
        """,
        )

        with tempfile.NamedTemporaryFile(suffix=f".png") as f:
            output_buffer = io.StringIO()
            with contextlib.redirect_stderr(output_buffer):
                self.run_filename(
                    "test_traceback_from_file.bot",
                    outputfile=f.name,
                    verbose=False,
                )
                actual_output = output = output_buffer.getvalue()

        self.assertEqual(actual_output, expected_output)


if __name__ == "__main__":
    unittest.main(buffer=False)
