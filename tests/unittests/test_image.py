import unittest
import sys

from pathlib import Path
from tests.unittests.helpers import ShoebotTestCase
from textwrap import dedent

from shoebot.core import CairoCanvas, CairoImageSink
from shoebot.data import Image


class TestImage(ShoebotTestCase):
    def test_svg_image(self):
        """
        Test that loading an svg image doesn't raise an exception (this was a bug).
        """
        input_image = self.test_input_dir / "input-image-svg.svg"
        actual_output = self.example_output_dir / "image-svg-actual.png"
        expected_output = self.example_input_dir / "image-svg-expected.png"
        code = dedent(
            f"""
        size(100, 100)
        image('{input_image}', 0, 0)
        """
        )

        self.run_code(code, outputfile=actual_output)

        self.assertReferenceImage(actual_output, expected_output)


if __name__ == "__main__":
    unittest.main()
