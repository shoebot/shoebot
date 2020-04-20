import unittest
import sys

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
        code = dedent(f"""
        size(100, 100)
        image('{test_dir}/input-image-svg.svg', 0, 0)
        """)

        self.run_code(code, outputfile=actual_output)

        self.assertOutputFile(actual_output)
        if sys.platform == "darwin":
            # Rendering on OSX is slightly different to the original Linux renders.
            self.assertOutputImagesAlmostEqual(actual_output, expected_output)
        else:
            # So far Linux output has been identical - this will probably need to
            # change to use image comparison.
            self.assertOutputFilesEqual(actual_output, expected_output)


if __name__ == "__main__":
    unittest.main()
