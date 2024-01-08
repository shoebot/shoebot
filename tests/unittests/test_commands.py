import unittest
from unittest.mock import patch, Mock, call

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

from shoebot.graphics import CLOSE
from shoebot.graphics import RCURVETO
from shoebot.graphics import ShoebotError
from shoebot.graphics import ARC
from shoebot.graphics import CURVETO
from shoebot.graphics import LINETO
from shoebot.graphics import RMOVETO
from shoebot.graphics import MOVETO
from shoebot.graphics import PathElement
from shoebot.graphics import RLINETO
from shoebot.graphics import RMOVETO


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
                "arcto(40, 40, 23, 90, 180)",
                [
                    PathElement(ARC, 40, 40, 23, radians(90), radians(180)),
                    PathElement(CLOSE, 40, 40),
                ],
            ),
        ],
    )
    @test_as_bot()
    def test_path_commands(self, cmd, expected_elements):
        """Run a command that should create a one element path.

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
        """Regression test to check that opening an image doesn't raise an
        exception."""
        input_image = f"{TEST_INPUT_DIR}/input-image-svg.svg"
        expected_output = f"{EXAMPLE_INPUT_DIR}/image-svg-expected.png"

        size(100, 100)
        image(input_image, 0, 0)

        flush_outputfile()
        self.assertReferenceImage(outputfile, expected_output)


class TestText(ShoebotTestCase):
    @test_as_bot()
    def test_text_saves_params(self):
        """Verify parameters are saved and returned by the expected
        properties."""
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

    @parameterized.expand(
        [
            (
                "DejaVu Sans Book",
                (1, 88.0, 87, 12),
            ),
            (
                "Liberation Sans Regular",
                (1, 88.0, 79, 12),
            ),
            (
                "Bitstream Vera Sans Roman",
                (1, 88.0, 87, 12),
            ),
        ],
    )
    @test_as_bot()
    def test_text_bounds(self, fontname, expected_bounds):
        """Check text.bounds() against expected values.

        Actual bounding box values may vary depending on font hinting, and DPI,
        so check within known values.

        This still may not be enough leniency, so this test may need to be changed
        just to verify the aspect ratio of the bounding box.
        """
        self.assertEqual(
            fontname, font(fontname), f"{fontname} is not available in the system",
        )

        t = text("Hello world", 0, 100, draw=False)

        self.assertBoundingBoxAlmostEqual(expected_bounds, t.bounds)

    @parameterized.expand(
        [
            (
                ("Letter spaced", 4, 5),
                {"tracking": 7},
                '<span letter_spacing="7168">Letter spaced</span>',
            ),
            (
                ("Underlined", 23, 25),
                {"underline": 3},
                '<span underline="3">Underlined</span>',
            ),
        ],
    )
    @patch("shoebot.graphics.typography.PangoCairo")
    @test_as_bot()
    def test_text_outputs_pango_text_spans(
        self, text_args, text_kwargs, expected_pango_text_span, pango_cairo,
    ):
        """For text calls that can only be For calls that should result in a
        call to set_markup in a Pango layout verify they arrive as expected."""
        # This test is a little implementation / specific, but gets close to verifying
        # the layout is used, and the markup is rendered.
        text(*text_args, **text_kwargs)

        # A layout should have been created.
        pango_cairo.create_layout.assert_called()
        layout = pango_cairo.create_layout.return_value

        layout.set_markup.assert_called_with(expected_pango_text_span)

        # Lastly, verify that flushing output causes show layout to be called.
        pango_cairo.show_layout.assert_not_called()

        flush_outputfile()
        pango_cairo.show_layout.assert_called()
        pango_cairo.reset_mock()

    @test_as_bot()
    def test_fontname_with_variants(self):
        """Verify that font() reads variable font values correctly."""
        font("Inconsolata", var_wdth=100, var_wght=200)
        fontstr = font()
        self.assertEqual(fontstr, "Inconsolata @wdth=100,wght=200")

        font("Inconsolata", vars={"wdth": 50, "wght": 400})
        fontstr = font()
        self.assertEqual(fontstr, "Inconsolata @wdth=50,wght=400")


class TestFontUtils(ShoebotTestCase):
    @test_as_bot()
    def test_fontnames_gives_output(self):
        """Verify that fontnames() gives a list as output."""
        output = fontnames()
        self.assertIsInstance(output, list)
        self.assertRegex(output[0], r"(.*)\s(.*)")


if __name__ == "__main__":
    unittest.main()
