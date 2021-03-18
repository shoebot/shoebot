import unittest

from math import radians
from parameterized import parameterized

# Add stubs for all shoebot APIs called:
from tests.unittests.stubs.extras import flush_outputfile
from tests.unittests.stubs.extras import outputfile
from tests.unittests.stubs.nodebox import relmoveto  # noqa
from tests.unittests.stubs.nodebox import moveto  # noqa
from tests.unittests.stubs.nodebox import beginpath  # noqa
from tests.unittests.stubs.nodebox import endpath  # noqa
from tests.unittests.stubs.nodebox import image  # noqa
from tests.unittests.stubs.nodebox import size  # noqa
from tests.unittests.stubs.nodebox import text  # noqa
from tests.unittests.helpers import EXAMPLE_INPUT_DIR
from tests.unittests.helpers import EXAMPLE_OUTPUT_DIR
from tests.unittests.helpers import ShoebotTestCase
from tests.unittests.helpers import test_as_bot
from tests.unittests.helpers import TEST_INPUT_DIR

from shoebot.data import CLOSE
from shoebot.data import RCURVETO
from shoebot.data import ShoebotError
from shoebot.data import ARC
from shoebot.data import CURVETO
from shoebot.data import LINETO
from shoebot.data import RMOVETO
from shoebot.data import MOVETO
from shoebot.data import PathElement
from shoebot.data import RLINETO
from shoebot.data import RMOVETO


class TestPath(ShoebotTestCase):
    @parameterized.expand(
        [
            (
                "moveto(40, 40)",
                [PathElement(MOVETO, 40, 40), PathElement(CLOSE, 40, 40)],
            ),
            (
                "relmoveto(40, 40)",
                [PathElement(RMOVETO, 40, 40), PathElement(CLOSE, 40, 40)],
            ),
            (
                "relmoveto(40, 40)",
                [PathElement(RMOVETO, 40, 40), PathElement(CLOSE, 40, 40)],
            ),
            (
                "lineto(40, 40)",
                [PathElement(LINETO, 40, 40), PathElement(CLOSE, 40, 40)],
            ),
            (
                "rellineto(40, 40)",
                [PathElement(RLINETO, 40, 40), PathElement(CLOSE, 40, 40)],
            ),
            (
                "curveto(40, 40, 60, 60, 80, 80)",
                [
                    PathElement(CURVETO, 40, 40, 60, 60, 80, 80),
                    PathElement(CLOSE, 80, 80),
                ],
            ),
            (
                "relcurveto(40, 40, 60, 60, 80, 80)",
                [
                    PathElement(RCURVETO, 40, 40, 60, 60, 80, 80),
                    PathElement(CLOSE, 80, 80),
                ],
            ),
            (
                "arc(40, 40, 23, 90, 180)",
                [
                    PathElement(ARC, 40, 40, 23, radians(90), radians(180)),
                    PathElement(CLOSE, 40, 40),
                ],
            ),
        ]
    )
    @test_as_bot()
    def test_path_commands(self, cmd, expected_elements):
        """
        Run a command that should create a one element path.

        - Verify it requires beginpath.
        - Run with begin + endpath, and verify the path contains the expected elements.
        """
        with self.assertRaises(ShoebotError):
            # ShoebotError should be raised if you haven't called beginpath
            eval(cmd)

        beginpath()
        eval(cmd)  # run path command, e.g: moveto(40, 40)
        path = endpath(draw=False)

        self.assertCountEqual(path, expected_elements)


class TestImage(ShoebotTestCase):
    @test_as_bot(outputfile=f"{EXAMPLE_OUTPUT_DIR}/image-svg-actual.png")
    def test_svg_image(self):
        """
        Regression test to check that opening an image doesn't raise an exception.
        """
        input_image = f"{TEST_INPUT_DIR}/input-image-svg.svg"
        expected_output = f"{EXAMPLE_INPUT_DIR}/image-svg-expected.png"

        size(100, 100)
        image(input_image, 0, 0)

        flush_outputfile()
        self.assertReferenceImage(outputfile, expected_output)


class TestText(ShoebotTestCase):
    @test_as_bot()
    def test_text_saves_params(self):
        """
        Verify parameters are saved and returned by the expected properties.
        """
        # There was a bug where using fontsize, weight or style was causing a crash.
        output_text = text(
            "Hello vector graphics",
            10,
            250,
            font="Bitstream Vera Bold Italic",
            fontsize=64,
        )

        self.assertEqual(output_text.text, "Hello vector graphics")
        self.assertEqual(output_text.x, 10)
        self.assertEqual(output_text.y, 250)
        self.assertEqual(output_text.font, "Bitstream Vera Bold Italic")
        self.assertEqual(output_text.fontsize, 64)


if __name__ == "__main__":
    unittest.main()
