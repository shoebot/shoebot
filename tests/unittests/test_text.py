import unittest

from shoebot.core.cairo_canvas import CairoCanvas
from shoebot.core.cairo_sink import CairoImageSink
from shoebot.grammar.nodebox import NodeBot


class TestText(unittest.TestCase):
    def setUp(self):
        sink = CairoImageSink("output-text.png")
        canvas = CairoCanvas(sink)
        self.bot = NodeBot(canvas=canvas)

    def test_text_saves_params(self):
        """Verify parameters are saved and returned by the expected
        properties."""
        # There was a bug where using fontsize, weight or style was causing a crash.
        text = self.bot.text(
            "Hello vector graphics",
            10,
            250,
            font="Bitstream Vera",
            fontsize=64,
        )

        self.assertEqual(text.text, "Hello vector graphics")
        self.assertEqual(text.x, 10)
        self.assertEqual(text.y, 250)
        self.assertEqual(text.font, "Bitstream Vera")
        self.assertEqual(text.fontsize, 64)


if __name__ == "__main__":
    unittest.main()
