"""Check if shoebot can create files in it's supported output formats and that
none are zero bytes long."""
import tempfile
import unittest

from parameterized import parameterized
from parameterized import parameterized_class

from tests.unittests.helpers import RUNNING_IN_CI
from tests.unittests.helpers import ShoebotTestCase
from tests.unittests.helpers import shoebot_named_testclass
from tests.unittests.helpers import shoebot_named_testfunction


@parameterized_class(
    [{"windowed": False}, {"windowed": True}],
    class_name_func=shoebot_named_testclass,
)
class TestOutputFormats(ShoebotTestCase):
    windowed = False  # False for headless, True for GUI

    @parameterized.expand(
        ["png", "ps", "pdf", "svg"],
        name_func=shoebot_named_testfunction,
    )
    def test_output_formats(self, file_format):
        """Run a simple bot for each supported output format and verify the
        output."""
        if RUNNING_IN_CI and file_format in ["png", "ps", "pdf"]:
            self.skipTest(f"{file_format} output was freezing github CI.")

        with tempfile.NamedTemporaryFile(suffix=f".{file_format}") as f:
            self.run_code("background(0)", outputfile=f.name, windowed=self.windowed)

            self.assertFileSize(f.name)


if __name__ == "__main__":
    unittest.main(buffer=False)
