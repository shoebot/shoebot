import unittest
from shoebot.data.basecolor import Color

TEST_COLOURS = (
    (128, (0.501961, 0.501961, 0.501961, 1.000000)),
    ((127,), (0.498039, 0.498039, 0.498039, 1.000000)),  # One value:  Grey Scale
    ((127, 64), (0.498039, 0.498039, 0.498039, 0.250979)),  # Two values: Grey Scale, Alpha
    ((0, 127, 255), (0.0, 0.498039, 1.0, 1.0)),
    ((0, 127, 255, 64), (0.0, 0.498039, 1.0, 0.250979)),
    ("#0000FF", (0.000000, 0.000000, 1.000000, 1.000000)),
    ("0000FF", (0.000000, 0.000000, 1.000000, 1.000000)),
    ("#0000FFFF", (0.000000, 0.000000, 1.000000, 1.000000)),
    ("000000ff", (0.000000, 0.000000, 0.000000, 1.000000)),
)


class ColorTest(unittest.TestCase):
    def assertColorEqual(self, result, expected, message=None):
        """
        check if difference is bigger than 0.0001, since floats
        are tricky things and behave a bit weird when comparing directly
        """
        for i, j in zip(result, expected):
            self.assertAlmostEqual(i, j, 5, message or "Colours are unequal: {} != {}".format(result, expected))

    def test_colors(self):
        """ this test checks with a 4 decimal point precision """
        # This test is originally from Nodebox basecolor
        for (value, expected) in TEST_COLOURS:
            color = Color(value, color_range=255)
            self.assertColorEqual(color, expected,
                                  "Value: {value} Expected {expected} Recieved {color}".format(color=color,
                                                                                               expected=expected,
                                                                                               value=value))


if __name__ == "__main__":
    unittest.main()
