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
        test_dir = Path(__file__).parent.absolute()

        actual_output = self.test_output_dir / "image-svg-actual.png"
        expected_output = self.test_output_dir / "image-svg-expected.png"
        code = dedent(
            f"""
        size(100, 100)
        image('{test_dir}/input-image-svg.svg', 0, 0)
        """
        )

        self.run_code(code, outputfile=actual_output)

        self.assertReferenceImage(actual_output, expected_output)


if __name__ == "__main__":
    unittest.main()
