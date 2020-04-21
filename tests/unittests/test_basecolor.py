import math
import unittest

from parameterized import parameterized, parameterized_class

from shoebot.data.basecolor import Color


class BaseColorTest(unittest.TestCase):
    def assertRGBAAlmostEqual(self, actual, expected, message=None):
        """
        This is ported from Nodebox 1 colors lib and improved.

        Check if difference is bigger than 0.0001, since floats
        are tricky things and behave a bit weird when comparing directly
        """
        almost_equal = True
        for actual_channel, expected_channel in zip(actual, expected):
            if not math.isclose(actual_channel, expected_channel, rel_tol=0.0001):
                almost_equal = False

        if not almost_equal:
            self.fail(
                message or f"RBGA values do not match: {actual} Expected {expected}"
            )

    @parameterized.expand(
        [
            (
                # Greyscale as single integer, expanded to RGB channels with alpha of 1.0.
                128,
                (0.501961, 0.501961, 0.501961, 1.000000),
            ),
            (
                # One digit grey scale:  Grey is expanded to RGB with alpha of 1.0.
                (127,),
                (0.498039, 0.498039, 0.498039, 1.000000),
            ),
            (
                # Two digit grey scale and Alpha:  Grey expanded to RGB channels with alpha of 1.0.
                (127, 64),
                (0.498039, 0.498039, 0.498039, 0.250979),
            ),
            (
                # Three digit decimal RGB, alpha of 1.0 is added by Color
                (0, 127, 255),
                (0.0, 0.498039, 1.0, 1.0),
            ),
            (
                # Three digit decimal RGB, alpha of 1.0 is added by Color
                (0, 127, 255, 64),
                (0.0, 0.498039, 1.0, 0.250979),
            ),
            (
                # Three digit hex with #, alpha of 1.0 is assumed by Color
                "#0000FF",
                (0.000000, 0.000000, 1.000000, 1.000000),
            ),
            (
                # Three digit hex without #, alpha of 1.0 is assumed by Color
                "0000FF",
                (0.000000, 0.000000, 1.000000, 1.000000),
            ),
            (
                # Four digit hex with #, alpha of 1.0 is assumed by Color
                "#0000FFFF",
                (0.000000, 0.000000, 1.000000, 1.000000),
            ),
            (
                # Four digit hex without #, alpha of 1.0 is assumed by Color
                "000000ff",
                (0.000000, 0.000000, 0.000000, 1.000000),
            ),
        ]
    )
    def test_rgb_color_formats(self, input_color, expected_rgba):
        """
        Test input colors in the RGB(A) colour space.
        """
        # This test was ported from nodebox 1, and could probably
        # be split into seperate tests.
        actual_rgba = Color(input_color, color_range=255)

        self.assertRGBAAlmostEqual(actual_rgba, expected_rgba)


if __name__ == "__main__":
    unittest.main()
